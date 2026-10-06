"""
Comprehensive ontology and taxonomy of technical, domain, and soft skills.
"""

from typing import Dict, List, Set
from app.models.student import SkillCategory

# Canonical skill name -> metadata (category, synonyms/aliases, domain)
SKILL_TAXONOMY: Dict[str, Dict] = {
    # Programming Languages
    "Python": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["python", "py", "python3"],
        "keywords": ["django", "flask", "fastapi", "pandas", "numpy", "pytorch"],
    },
    "Java": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["java", "jvm", "core java"],
        "keywords": ["spring", "springboot", "hibernate", "maven", "gradle"],
    },
    "C++": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["c++", "cpp"],
        "keywords": ["stl", "pointers", "cmake", "cuda", "embedded"],
    },
    "C#": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["c#", "csharp", ".net"],
        "keywords": ["asp.net", "unity", "linq", "wpf"],
    },
    "JavaScript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["javascript", "js", "ecmascript"],
        "keywords": ["node", "express", "react", "vue", "frontend"],
    },
    "TypeScript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["typescript", "ts"],
        "keywords": ["angular", "react", "next.js", "nest.js"],
    },
    "Go": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["golang", "go lang"],
        "keywords": ["goroutines", "grpc", "microservices"],
    },
    "Rust": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["rust", "rustlang"],
        "keywords": ["cargo", "memory safety", "wasm"],
    },
    "SQL": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "aliases": ["sql", "structured query language"],
        "keywords": ["postgres", "mysql", "queries", "joins", "normalization"],
    },

    # AI / Machine Learning
    "Machine Learning": {
        "category": SkillCategory.AI_ML,
        "aliases": ["machine learning", "ml", "statistical learning"],
        "keywords": ["scikit-learn", "regression", "classification", "clustering", "random forest"],
    },
    "Deep Learning": {
        "category": SkillCategory.AI_ML,
        "aliases": ["deep learning", "neural networks", "dl"],
        "keywords": ["pytorch", "tensorflow", "keras", "backpropagation", "cnn", "rnn"],
    },
    "Computer Vision": {
        "category": SkillCategory.AI_ML,
        "aliases": ["computer vision", "cv", "image processing", "object detection"],
        "keywords": ["opencv", "yolo", "segmentation", "resnet", "pillow"],
    },
    "Natural Language Processing": {
        "category": SkillCategory.AI_ML,
        "aliases": ["natural language processing", "nlp", "text analytics", "llm"],
        "keywords": ["transformers", "huggingface", "bert", "spacy", "tokenization", "gemini", "langchain"],
    },
    "Reinforcement Learning": {
        "category": SkillCategory.AI_ML,
        "aliases": ["reinforcement learning", "rl"],
        "keywords": ["q-learning", "policy gradient", "gymnasium", "stable-baselines"],
    },
    "PyTorch": {
        "category": SkillCategory.AI_ML,
        "aliases": ["pytorch", "torch"],
        "keywords": ["torchvision", "cuda", "tensors"],
    },
    "TensorFlow": {
        "category": SkillCategory.AI_ML,
        "aliases": ["tensorflow", "tf"],
        "keywords": ["keras", "tensorboard", "tflite"],
    },

    # Data & Databases
    "PostgreSQL": {
        "category": SkillCategory.DATA_DATABASE,
        "aliases": ["postgresql", "postgres", "psql"],
        "keywords": ["relational", "acid", "indices", "sql"],
    },
    "MongoDB": {
        "category": SkillCategory.DATA_DATABASE,
        "aliases": ["mongodb", "mongo"],
        "keywords": ["nosql", "document database", "bson"],
    },
    "Redis": {
        "category": SkillCategory.DATA_DATABASE,
        "aliases": ["redis", "in-memory cache"],
        "keywords": ["caching", "pubsub", "key-value"],
    },
    "Data Engineering": {
        "category": SkillCategory.DATA_DATABASE,
        "aliases": ["data engineering", "etl", "data pipeline"],
        "keywords": ["airflow", "spark", "kafka", "hadoop", "polars", "dbt"],
    },
    "Data Analysis": {
        "category": SkillCategory.DATA_DATABASE,
        "aliases": ["data analysis", "eda", "data visualization"],
        "keywords": ["pandas", "matplotlib", "seaborn", "tableau", "power bi"],
    },

    # Web & Mobile
    "React": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["react", "react.js", "reactjs"],
        "keywords": ["jsx", "hooks", "redux", "nextjs", "frontend"],
    },
    "Next.js": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["next.js", "nextjs"],
        "keywords": ["ssr", "ssg", "react", "app router"],
    },
    "Node.js": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["node.js", "nodejs", "node"],
        "keywords": ["express", "npm", "backend", "event loop"],
    },
    "FastAPI": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["fastapi", "fast api"],
        "keywords": ["pydantic", "starlette", "rest api", "openapi", "swagger"],
    },
    "Django": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["django", "django rest framework", "drf"],
        "keywords": ["orm", "mvc", "mvt", "python web"],
    },
    "Flutter": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["flutter", "dart mobile"],
        "keywords": ["dart", "cross-platform", "ios", "android"],
    },
    "UI/UX Design": {
        "category": SkillCategory.WEB_MOBILE,
        "aliases": ["ui/ux", "ui design", "ux design", "figma", "wireframing"],
        "keywords": ["prototyping", "design system", "user research"],
    },

    # Cloud & DevOps
    "Docker": {
        "category": SkillCategory.CLOUD_DEVOPS,
        "aliases": ["docker", "containerization"],
        "keywords": ["dockerfile", "docker-compose", "containers"],
    },
    "Kubernetes": {
        "category": SkillCategory.CLOUD_DEVOPS,
        "aliases": ["kubernetes", "k8s"],
        "keywords": ["pods", "deployments", "helm", "orchestration"],
    },
    "AWS": {
        "category": SkillCategory.CLOUD_DEVOPS,
        "aliases": ["aws", "amazon web services"],
        "keywords": ["s3", "ec2", "lambda", "dynamodb", "cloudformation"],
    },
    "Google Cloud Platform": {
        "category": SkillCategory.CLOUD_DEVOPS,
        "aliases": ["gcp", "google cloud"],
        "keywords": ["bigquery", "cloud run", "gcs", "gke"],
    },
    "CI/CD": {
        "category": SkillCategory.CLOUD_DEVOPS,
        "aliases": ["ci/cd", "continuous integration", "devops pipeline"],
        "keywords": ["github actions", "gitlab ci", "jenkins"],
    },

    # Systems & IoT
    "IoT / Embedded Systems": {
        "category": SkillCategory.SYSTEMS_IOT,
        "aliases": ["iot", "internet of things", "embedded systems", "arduino", "raspberry pi"],
        "keywords": ["sensors", "microcontrollers", "mqtt", "gpio", "hardware"],
    },
    "Cybersecurity": {
        "category": SkillCategory.SYSTEMS_IOT,
        "aliases": ["cybersecurity", "security", "infosec", "penetration testing"],
        "keywords": ["cryptography", "owasp", "network security", "vulnerability"],
    },

    # Soft Skills & Roles
    "Project Leadership": {
        "category": SkillCategory.SOFT_SKILL,
        "aliases": ["leadership", "team lead", "project management", "scrum master"],
        "keywords": ["coordination", "agile", "sprint planning", "mentoring"],
    },
    "Technical Documentation": {
        "category": SkillCategory.SOFT_SKILL,
        "aliases": ["technical writing", "documentation", "docs"],
        "keywords": ["markdown", "api docs", "architecture diagram", "specifications"],
    },
    "Presentation & Communication": {
        "category": SkillCategory.SOFT_SKILL,
        "aliases": ["presentation", "communication", "public speaking"],
        "keywords": ["demo", "pitch", "slides", "stakeholder communication"],
    },
}


def find_canonical_skill(text: str) -> str | None:
    """Finds canonical skill name matching alias or text substring."""
    clean = text.lower().strip()
    for canonical, data in SKILL_TAXONOMY.items():
        if clean == canonical.lower():
            return canonical
        for alias in data["aliases"]:
            if clean == alias.lower():
                return canonical
    return None
