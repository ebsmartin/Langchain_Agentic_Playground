from typing import List, Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Summary(BaseModel):
    summary: str = Field(
        description="A concise summary of the LinkedIn profile, including name, job title, education, contact info, work experience, skills, and image URLs."
    )
    facts: List[str] = Field(
        description="A list of key facts extracted from the LinkedIn profile, such as job title, education, contact information, and skills."
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Summary object to a dictionary."""
        return {
            "summary": self.summary,
            "facts": self.facts
        }

summary_parser = PydanticOutputParser(pydantic_object=Summary)