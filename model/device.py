import pydantic


class Device(pydantic.BaseModel):
    ip: str
    passed: bool = False
    on: bool = False
    turn_order: int = 0
