#!/usr/bin/env python3
"""
Enhanced LangGraph memory system with:
1. Tag extraction from existing content
2. Semantic relationship detection
3. OpenClaw heartbeat integration
"""

import os
import re
import json
import glob
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib

# LangGraph imports
from langgraph.graph import StateGraph, END

# For semantic similarity (fallback to simple if not available)
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("Warning: sentence-transformers not available, using keyword-based similarity")

@dataclass
class EnhancedMemoryChunk:
    """Enhanced memory chunk with semantic capabilities."""
    id: str
    content: str
    source_file: str
    line_range: tuple[int, int]
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)  # Extracted keywords
    embedding: Optional[List[float]] = None  # Semantic embedding
    relationships: Dict[str, float] = field(default_factory=dict)  # ID -> similarity score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source_file": self.source_file,
            "line_range": self.line_range,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "keywords": self.keywords,
            "relationships": {k: float(v) for k, v in self.relationships.items()}
        }

class EnhancedMemoryGraph:
    """Enhanced memory graph with semantic capabilities."""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.memory_dir = os.path.join(workspace_path, "memory")
        self.memory_file = os.path.join(workspace_path, "MEMORY.md")
        
        # Initialize semantic model if available
        self.semantic_model = None
        if SEMANTIC_AVAILABLE:
            try:
                # Use E5-small-v2 (better multilingual, instruction-aware)
                self.semantic_model = SentenceTransformer('intfloat/e5-small-v2')
                print("Semantic model loaded: intfloat/e5-small-v2 (E5-small-v2)")
            except Exception as e:
                print(f"Failed to load E5 model: {e}")
                # Fallback to all-MiniLM-L6-v2
                try:
                    self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                    print("Fallback semantic model loaded: all-MiniLM-L6-v2")
                except Exception as e2:
                    print(f"Failed to load fallback model: {e2}")
                    self.semantic_model = None
        
        # Keyword extraction patterns
        self.keyword_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Proper nouns
            r'\b(\w{6,})\b',  # Longer words
            r'#(\w+)',  # Hashtags
        ]
        
        # Common words to exclude
        self.stop_words = {
            'the', 'and', 'to', 'of', 'a', 'in', 'is', 'that', 'for', 'on', 
            'with', 'as', 'by', 'an', 'be', 'this', 'or', 'at', 'from', 'but',
            'not', 'are', 'it', 'if', 'you', 'was', 'we', 'have', 'has', 'had'
        }
        
        # Tag rules for automatic tagging (based on memory_tagger.py)
        self.tag_rules = {
            'voice': ["voice", "accent", "tts", "audio", "whisper", "transcription", "speech", "sound"],
            'disk': ["disk", "space", "gb", "cleanup", "cache", "delete", "storage", "temp", "tmp"],
            'cron': ["cron", "schedule", "daily", "job", "automated", "scheduled", "cronjob"],
            'heartbeat': ["heartbeat", "monitoring", "check", "health", "status"],
            'audio': ["audio", "ogg", "mp3", "sound", "listen", "hear", "play"],
            'tts': ["tts", "text-to-speech", "synthes", "voice"],
            'transcription': ["transcription", "whisper", "speech-to-text", "transcribe"],
            'cleanup': ["cleanup", "delete", "remove", "prune", "optimize", "free", "space"],
            'decision': ["decision", "choose", "option", "select", "prefer"],
            'error': ["error:", "failed to", "could not", "unable to", "traceback", "exception:", 
                      "crash", "fatal", "segmentation fault", "syntax error", "import error"],
            'success': ["success", "completed", "working", "fixed", "resolved", "successful"],
            'todo': ["todo", "task", "pending", "need", "waiting", "outstanding"],
            'system': ["system", "status", "monitor", "performance", "optimize", "configuration"],
            'memory': ["memory", "flush", "compaction", "recall", "remember", "embedding", "search"],
            'conversation': ["conversation", "chat", "discuss", "talk", "message", "reply", "response"],
            'gpu': ["gpu", "cuda", "nvidia", "gpu", "acceleration", "torch"],
            'cpu': ["cpu", "processor", "compute", "performance"],
            'network': ["network", "internet", "api", "http", "web", "url"],
            'security': ["security", "auth", "password", "token", "key", "access"],
            'development': ["development", "code", "script", "program", "implementation", "prototype"],
            'question': ["question", "ask", "query", "what", "how", "why"],
            'answer': ["answer", "response", "reply", "solution", "explanation"],
        }
        
        # Initialize
        self.memories: Dict[str, EnhancedMemoryChunk] = {}
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> memory IDs
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)  # keyword -> memory IDs
        
        self._load_and_enhance_memories()
        self.graph = self._build_enhanced_graph()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using multiple strategies."""
        keywords = set()
        
        # Strategy 1: Extract proper nouns and multi-word phrases
        for pattern in self.keyword_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if len(match) > 3 and match.lower() not in self.stop_words:
                    keywords.add(match.lower())
        
        # Strategy 2: Split by non-alphanumeric and take meaningful words
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if (len(word) > 4 and 
                word not in self.stop_words and
                not word.isdigit()):
                keywords.add(word)
        
        # Strategy 3: Extract from markdown headers and bold text
        headers = re.findall(r'#+\s+(.+)', text)
        for header in headers:
            words = header.split()
            for word in words:
                if len(word) > 3 and word.lower() not in self.stop_words:
                    keywords.add(word.lower())
        
        # Strategy 4: Extract from bullet points (often contain key terms)
        bullets = re.findall(r'[-*•]\s+(.+)', text)
        for bullet in bullets:
            words = bullet.split()
            for word in words:
                if len(word) > 3 and word.lower() not in self.stop_words:
                    keywords.add(word.lower())
        
        return list(keywords)[:20]  # Limit to top 20
    
    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract tags from content using hashtags, patterns, and keyword rules."""
        tags = set()
        content_lower = content.lower()
        
        # 1. Extract explicit hashtags
        hashtags = re.findall(r'#(\w+)', content)
        tags.update(hashtags)
        
        # 2. Extract from common patterns in our memory files (legacy patterns)
        patterns = [
            (r'(?:BA|MA|PhD)[-\s]?(?:thesis|Thesis)', ['thesis', 'academic']),
            (r'OpenClaw', ['openclaw', 'system']),
            (r'Telegram', ['telegram', 'communication']),
            (r'GitHub', ['github', 'code']),
            (r'Notion', ['notion', 'documentation']),
            (r'LangGraph', ['langgraph', 'memory']),
            (r'Heartbeat', ['heartbeat', 'monitoring']),
            (r'Cron', ['cron', 'scheduling']),
            (r'API', ['api', 'integration']),
            (r'Model', ['model', 'ai']),
        ]
        
        for pattern, tag_list in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                tags.update(tag_list)
        
        # 3. Apply comprehensive tag rules based on keyword matching
        for tag, keywords in self.tag_rules.items():
            for keyword in keywords:
                if keyword in content_lower:
                    tags.add(tag)
                    break  # One keyword match is enough for the tag
        
        # 4. Ensure backward compatibility with content-type tags
        # (These are already covered by tag_rules, but keep for safety)
        # Improved error detection: look for actual error patterns, not just the word "error"
        actual_error_patterns = [
            'error:', 'Error:', 'Traceback', 'failed to', 'could not',
            'unable to', 'crash', 'fatal error', 'segmentation fault',
            'syntax error', 'import error', '[ERROR]'
        ]
        if any(pattern.lower() in content_lower for pattern in actual_error_patterns):
            tags.add('error')
        
        if any(word in content_lower for word in ['todo', 'task', 'pending', 'need']):
            tags.add('todo')
        
        if any(word in content_lower for word in ['success', 'working', 'fixed', 'resolved']):
            tags.add('success')
        
        if any(word in content_lower for word in ['security', 'audit', 'warning', 'risk']):
            tags.add('security')
        
        return list(tags)
    
    def _is_meaningful_chunk(self, chunk_text: str) -> bool:
        """
        Check if a chunk contains meaningful content (not empty, not just headers).
        
        Args:
            chunk_text: The chunk text to evaluate
            
        Returns:
            True if the chunk is meaningful for embedding and search
        """
        # Check 1: Not empty or whitespace-only
        if not chunk_text or not chunk_text.strip():
            return False
        
        text = chunk_text.strip()
        
        # Check 2: Minimum length (adjustable)
        if len(text) < 40:  # Slightly higher than 30 to filter short headers
            # Check if it's just a header (starts with # and has few words)
            lines = text.split('\n')
            if len(lines) == 1 and text.startswith('#'):
                # Single line that's a header - likely not meaningful alone
                return False
        
        # Check 3: Has actual content (not just metadata, frontmatter, etc.)
        # Count words (rough estimate)
        words = text.split()
        if len(words) < 10:  # Very short content
            # Might be a header or brief note
            return False
        
        # Check 4: Not just code blocks or special markers
        if text.startswith('```') or '---' in text[:20]:
            return False
        
        return True
    
    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """Compute semantic embedding for text."""
        if not self.semantic_model:
            return None
        
        try:
            # Use first 512 characters for efficiency
            truncated = text[:512]
            embedding = self.semantic_model.encode(truncated)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding computation failed: {e}")
            return None
    
    def _calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        if not emb1 or not emb2:
            return 0.0
        
        try:
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            norm1 = sum(a * a for a in emb1) ** 0.5
            norm2 = sum(b * b for b in emb2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    def _load_and_enhance_memories(self):
        """Load and enhance existing memories."""
        processed_files = set()
        
        # 1. Load from MEMORY.md (long-term curated memory)
        if os.path.exists(self.memory_file):
            self._parse_and_enhance_file(self.memory_file, "MEMORY.md")
            processed_files.add(self.memory_file)
        
        # 2. Load from daily memory files (session logs)
        if os.path.exists(self.memory_dir):
            for filename in os.listdir(self.memory_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.memory_dir, filename)
                    if filepath not in processed_files:
                        self._parse_and_enhance_file(filepath, f"memory/{filename}")
                        processed_files.add(filepath)
        
        # 3. Load configuration files (personality, protocols, tools)
        config_files = [
            "SOUL.md", "AGENTS.md", "TOOLS.md", "IDENTITY.md",
            "HEARTBEAT.md", "USER.md", "PROJECT.md"
        ]
        for config_file in config_files:
            filepath = os.path.join(self.workspace_path, config_file)
            if os.path.exists(filepath) and filepath not in processed_files:
                self._parse_and_enhance_file(filepath, config_file)
                processed_files.add(filepath)
        
        # 4. Load thesis chapters and writing
        thesis_patterns = [
            "ba_thesis_chapter*.md",
            "writing/*.md"
        ]
        for pattern in thesis_patterns:
            for filepath in glob.glob(os.path.join(self.workspace_path, pattern)):
                if filepath not in processed_files:
                    # Use relative path for source name
                    rel_path = os.path.relpath(filepath, self.workspace_path)
                    self._parse_and_enhance_file(filepath, rel_path)
                    processed_files.add(filepath)
        
        # 5. Load skills documentation (SKILL.md files)
        skill_pattern = os.path.join(self.workspace_path, "skills", "*", "SKILL.md")
        for filepath in glob.glob(skill_pattern):
            if filepath not in processed_files:
                # Extract skill name from path
                skill_dir = os.path.basename(os.path.dirname(filepath))
                source_name = f"skills/{skill_dir}/SKILL.md"
                self._parse_and_enhance_file(filepath, source_name)
                processed_files.add(filepath)
        
        # Compute embeddings and relationships
        self._compute_embeddings()
        self._compute_relationships()
    
    def _parse_and_enhance_file(self, filepath: str, source: str):
        """Parse a file and create enhanced memory chunks using line-based chunking."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract date from filename
            if source.startswith("memory/"):
                date_str = os.path.basename(source).replace(".md", "")
                try:
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # State for chunking
            current_chunk_lines = []
            current_start = 1
            in_code_block = False
            in_frontmatter = False
            frontmatter_delimiter_count = 0
            chunk_index = 0
            
            for i, line in enumerate(lines, 1):
                # Handle frontmatter (lines between ---)
                stripped_line = line.strip()
                if stripped_line == "---":
                    frontmatter_delimiter_count += 1
                    if frontmatter_delimiter_count == 1:
                        in_frontmatter = True
                        continue
                    elif frontmatter_delimiter_count == 2:
                        in_frontmatter = False
                        continue
                
                if in_frontmatter:
                    continue
                
                # Skip code blocks
                if stripped_line.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                
                if in_code_block:
                    continue
                
                # Determine if this line starts a new section (## or ###)
                is_section_header = stripped_line.startswith("##")
                # Also consider single # headers but only if they're at the beginning of a line
                # and not inside lists or other contexts
                is_top_header = stripped_line.startswith("# ") and not stripped_line.startswith("##")
                
                # Start new chunk on section headers or after 15 lines (adjustable)
                is_large_chunk = len(current_chunk_lines) >= 15
                
                if (is_section_header or is_top_header or is_large_chunk) and current_chunk_lines:
                    # Save current chunk
                    chunk_text = "".join(current_chunk_lines).strip()
                    
                    # Skip empty, very short, or header-only chunks
                    if self._is_meaningful_chunk(chunk_text):
                        chunk_id = f"{source.replace('/', '_')}_{chunk_index}"
                        
                        # Extract tags and keywords from this chunk
                        tags = self._extract_tags_from_content(chunk_text)
                        keywords = self._extract_keywords(chunk_text)
                        
                        memory = EnhancedMemoryChunk(
                            id=chunk_id,
                            content=chunk_text,
                            source_file=source,
                            line_range=(current_start, i-1),
                            timestamp=timestamp,
                            tags=tags,
                            keywords=keywords,
                            embedding=None,
                            relationships={}
                        )
                        
                        self.memories[chunk_id] = memory
                        
                        # Update indices
                        for tag in tags:
                            self.tag_index[tag].add(chunk_id)
                        for keyword in keywords:
                            self.keyword_index[keyword].add(chunk_id)
                        
                        chunk_index += 1
                    
                    # Start new chunk
                    current_chunk_lines = []
                    current_start = i
                
                current_chunk_lines.append(line)
            
            # Add final chunk
            if current_chunk_lines:
                chunk_text = "".join(current_chunk_lines).strip()
                if self._is_meaningful_chunk(chunk_text):
                    chunk_id = f"{source.replace('/', '_')}_{chunk_index}"
                    
                    tags = self._extract_tags_from_content(chunk_text)
                    keywords = self._extract_keywords(chunk_text)
                    
                    memory = EnhancedMemoryChunk(
                        id=chunk_id,
                        content=chunk_text,
                        source_file=source,
                        line_range=(current_start, len(lines)),
                        timestamp=timestamp,
                        tags=tags,
                        keywords=keywords,
                        embedding=None,
                        relationships={}
                    )
                    
                    self.memories[chunk_id] = memory
                    
                    for tag in tags:
                        self.tag_index[tag].add(chunk_id)
                    for keyword in keywords:
                        self.keyword_index[keyword].add(chunk_id)
        
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            import traceback
            traceback.print_exc()
    
    def _compute_embeddings(self):
        """Compute embeddings for all memories."""
        print(f"Computing embeddings for {len(self.memories)} memories...")
        
        for memory_id, memory in self.memories.items():
            if memory.embedding is None:
                memory.embedding = self._compute_embedding(memory.content)
        
        print("Embeddings computed.")
    
    def _compute_relationships(self, threshold: float = 0.3):
        """Compute relationships between memories."""
        print(f"Computing relationships (threshold: {threshold})...")
        
        memory_ids = list(self.memories.keys())
        embeddings = {}
        
        # Get embeddings that exist
        for mem_id in memory_ids:
            emb = self.memories[mem_id].embedding
            if emb:
                embeddings[mem_id] = emb
        
        # Compute similarities
        for i, mem_id1 in enumerate(memory_ids):
            emb1 = embeddings.get(mem_id1)
            if not emb1:
                continue
            
            for mem_id2 in memory_ids[i+1:]:
                emb2 = embeddings.get(mem_id2)
                if not emb2:
                    continue
                
                similarity = self._calculate_similarity(emb1, emb2)
                
                if similarity > threshold:
                    self.memories[mem_id1].relationships[mem_id2] = similarity
                    self.memories[mem_id2].relationships[mem_id1] = similarity
        
        print(f"Relationships computed.")
    
    def _update_relationships_for_memory(self, memory_id: str, threshold: float = 0.3):
        """Update relationships for a single memory."""
        if memory_id not in self.memories:
            return
        
        memory = self.memories[memory_id]
        if not memory.embedding:
            return
        
        for other_id, other_memory in self.memories.items():
            if other_id == memory_id:
                continue
            
            if other_memory.embedding:
                similarity = self._calculate_similarity(memory.embedding, other_memory.embedding)
                if similarity > threshold:
                    memory.relationships[other_id] = similarity
                    other_memory.relationships[memory_id] = similarity
    
    def _build_enhanced_graph(self) -> StateGraph:
        """Build enhanced LangGraph workflow."""
        
        class EnhancedMemoryState(TypedDict):
            query: Optional[str]
            new_memory_text: Optional[str]
            retrieved_memories: List[Dict[str, Any]]
            similar_memories: List[Dict[str, Any]]
            summary: Optional[str]
            action_taken: Optional[str]
            tags_found: List[str]
        
        def ingest_node(state: EnhancedMemoryState) -> EnhancedMemoryState:
            """Ingest and enhance new memory."""
            if state.get("new_memory_text"):
                # Create enhanced memory chunk
                chunk_id = f"new_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                tags = self._extract_tags_from_content(state["new_memory_text"])
                keywords = self._extract_keywords(state["new_memory_text"])
                embedding = self._compute_embedding(state["new_memory_text"])
                
                memory = EnhancedMemoryChunk(
                    id=chunk_id,
                    content=state["new_memory_text"],
                    source_file="new_input",
                    line_range=(0, 1),
                    timestamp=datetime.now(),
                    tags=tags,
                    keywords=keywords,
                    embedding=embedding,
                    relationships={}
                )
                
                self.memories[chunk_id] = memory
                
                # Update indices
                for tag in tags:
                    self.tag_index[tag].add(chunk_id)
                for keyword in keywords:
                    self.keyword_index[keyword].add(chunk_id)
                
                # Compute new relationships
                self._update_relationships_for_memory(chunk_id)
                
                state["action_taken"] = f"Ingested and enhanced new memory: {chunk_id}"
                state["tags_found"] = tags
            
            return state
        
        def retrieve_node(state: EnhancedMemoryState) -> EnhancedMemoryState:
            """Retrieve memories using multiple strategies."""
            query = state.get("query")
            if not query:
                return state
            
            retrieved = []
            
            # Strategy 1: Keyword matching
            query_lower = query.lower()
            for memory in self.memories.values():
                if (query_lower in memory.content.lower() or
                    any(query_lower in keyword for keyword in memory.keywords)):
                    retrieved.append(memory.to_dict())
            
            # Strategy 2: Tag matching
            if query_lower in self.tag_index:
                for mem_id in self.tag_index[query_lower]:
                    if mem_id in self.memories:
                        retrieved.append(self.memories[mem_id].to_dict())
            
            # Remove duplicates
            seen_ids = set()
            unique_retrieved = []
            for mem in retrieved:
                if mem["id"] not in seen_ids:
                    seen_ids.add(mem["id"])
                    unique_retrieved.append(mem)
            
            state["retrieved_memories"] = unique_retrieved
            state["action_taken"] = f"Retrieved {len(unique_retrieved)} memories"
            
            return state
        
        def semantic_node(state: EnhancedMemoryState) -> EnhancedMemoryState:
            """Find semantically similar memories."""
            query = state.get("query")
            if not query or not self.semantic_model:
                return state
            
            # Compute query embedding
            query_embedding = self._compute_embedding(query)
            if not query_embedding:
                return state
            
            # Find similar memories
            similar = []
            for memory in self.memories.values():
                if memory.embedding:
                    similarity = self._calculate_similarity(query_embedding, memory.embedding)
                    if similarity > 0.4:  # Higher threshold for semantic similarity
                        mem_dict = memory.to_dict()
                        mem_dict["similarity_score"] = float(similarity)
                        similar.append(mem_dict)
            
            # Sort by similarity
            similar.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            state["similar_memories"] = similar[:5]  # Top 5
            
            return state
        
        def summarize_node(state: EnhancedMemoryState) -> EnhancedMemoryState:
            """Generate enhanced summary."""
            # Get recent memories
            week_ago = datetime.now() - timedelta(days=7)
            recent = [m for m in self.memories.values() if m.timestamp > week_ago]
            
            if recent:
                # Count by tags
                tag_counts = defaultdict(int)
                for memory in recent:
                    for tag in memory.tags:
                        tag_counts[tag] += 1
                
                # Generate summary
                lines = [f"Enhanced Summary (last 7 days): {len(recent)} memories"]
                lines.append(f"Total memories in system: {len(self.memories)}")
                lines.append(f"Total tags: {len(self.tag_index)}")
                lines.append(f"Total keywords: {len(self.keyword_index)}")
                
                if tag_counts:
                    lines.append("\nTop tags:")
                    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                        lines.append(f"  - #{tag}: {count}")