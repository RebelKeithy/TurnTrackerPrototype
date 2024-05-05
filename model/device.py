import pydantic


class Device(pydantic.BaseModel):
    passed: bool = False
    on: bool = False
    turn_order: int = 0
