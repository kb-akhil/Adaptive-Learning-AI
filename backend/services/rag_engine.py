# ============================================================
# services/rag_engine.py
# Subject-independent RAG Engine.
#
# Design:
#   - GENERIC_TEMPLATES  → work for any topic, any subject
#   - Subject-specific templates (CN_TEMPLATES, etc.) are only
#     activated when the topic vocabulary matches that subject.
#
# To add a new subject later:
#   1. Add its VOCABULARY set  (e.g. DS_VOCABULARY)
#   2. Add its TEMPLATES list  (e.g. DS_TEMPLATES)
#   3. Add a detection branch  in _detect_domain()
# ============================================================
import re

# ============================================================
# Generic templates — subject-independent
# {topic} is replaced with the actual topic at retrieval time
# ============================================================
GENERIC_TEMPLATES = [
    {"type": "mcq", "pattern": "Generate an MCQ question about {topic}"},
    {"type": "mcq", "pattern": "Generate a multiple choice question testing understanding of {topic}"},
    {"type": "mcq", "pattern": "Create a definition-based MCQ about {topic}"},
    {"type": "mcq", "pattern": "Generate an application-based MCQ about {topic}"},
    {"type": "tf",  "pattern": "Generate a True or False question about {topic}"},
    {"type": "tf",  "pattern": "Create a True/False question testing knowledge of {topic}"},
]

# ============================================================
# Computer Networks templates — activated only for CN topics
# The model was trained on these exact prompt formats
# ============================================================
CN_TEMPLATES = [
    {"type": "mcq", "pattern": "Generate a Computer Networks MCQ about {topic}"},
    {"type": "mcq", "pattern": "Generate a Computer Networks MCQ about {topic} protocol"},
    {"type": "mcq", "pattern": "Generate a Computer Networks MCQ about {topic} algorithm"},
    {"type": "tf",  "pattern": "Generate a Computer Networks True/False about {topic}"},
    {"type": "tf",  "pattern": "Generate a Computer Networks True/False statement about {topic}"},
]

# Vocabulary that signals Computer Networks content
CN_VOCABULARY = {
    "routing","switching","tcp","udp","ip","osi","dns","http","https",
    "ethernet","bandwidth","latency","protocol","packet","frame","subnet",
    "gateway","firewall","vpn","socket","port","mac","congestion",
    "flow control","error detection","checksum","arp","icmp","dhcp",
    "nat","ospf","bgp","rip","vlan","handshake","sliding window",
    "distance vector","link state","dijkstra","bellman","network",
    "topology","wireless","wifi"
}

# ============================================================
# Add future subjects here following the same pattern:
#
# DS_TEMPLATES = [
#     {"type":"mcq","pattern":"Generate a Data Structures MCQ about {topic}"},
#     {"type":"tf", "pattern":"Generate a Data Structures True/False about {topic}"},
# ]
# DS_VOCABULARY = {"array","linked list","tree","graph","stack","queue",...}
# ============================================================


class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    Given any topic, selects the best prompt template and returns
    filled prompts ready to be sent to the FLAN-T5 model.
    """

    def retrieve(self, topic: str, top_k: int = 2) -> list:
        """
        Return top_k question prompts for any topic.

        For recognized subjects (CN, etc.) → subject-specific templates
        For all other subjects             → generic templates
        Always returns at least 1 MCQ + 1 TF for balanced assessment.
        """
        topic  = topic.strip()
        domain = self._detect_domain(topic)

        bank = CN_TEMPLATES if domain == "computer_networks" else GENERIC_TEMPLATES
        # Future: elif domain == "data_structures": bank = DS_TEMPLATES

        mcq_bank = [t for t in bank if t["type"] == "mcq"]
        tf_bank  = [t for t in bank if t["type"] == "tf"]

        results = []
        if mcq_bank:
            results.append({
                "prompt": mcq_bank[0]["pattern"].replace("{topic}", topic),
                "type":   "mcq"
            })
        if tf_bank and top_k > 1:
            results.append({
                "prompt": tf_bank[0]["pattern"].replace("{topic}", topic),
                "type":   "tf"
            })
        # Fill remaining with more MCQs if needed
        for t in mcq_bank[1:]:
            if len(results) >= top_k:
                break
            results.append({
                "prompt": t["pattern"].replace("{topic}", topic),
                "type":   "mcq"
            })

        print(f"[RAG] '{topic}' → domain:{domain} → {len(results)} prompts")
        return results[:top_k]

    def _detect_domain(self, topic: str) -> str:
        """
        Detect subject domain from topic vocabulary.
        This is the ONLY subject-aware function in the codebase.
        Everything else is fully generic.
        """
        t = topic.lower()
        if any(kw in t for kw in CN_VOCABULARY):
            return "computer_networks"
        # Future subjects:
        # if any(kw in t for kw in DS_VOCABULARY): return "data_structures"
        return "generic"


# Singleton reused across all requests
rag_engine = RAGEngine()