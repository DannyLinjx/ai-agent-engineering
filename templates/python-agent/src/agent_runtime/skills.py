from dataclasses import dataclass

@dataclass(frozen=True)
class SkillDescriptor:
    name: str
    description: str
    root: str
    trust: str

class SkillLoader:
    def __init__(self, catalog: list[SkillDescriptor]) -> None: self.catalog = catalog
    def select(self, query: str, limit: int = 3) -> list[SkillDescriptor]:
        terms = query.lower().split()
        return [s for s in self.catalog if any(t in s.description.lower() for t in terms)][:limit]
