from pydantic import BaseModel


class SchemeDTO(BaseModel):
    
    scheme_id: int
    scheme_name: str
    one_year_return: float
    three_year_return: float 
    five_year_return: float 