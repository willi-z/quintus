from pydantic import BaseModel


class Pointers(BaseModel):
    names: int = None
    prefix: int = None
    start: int = None
    units: int = None

    # def update(self, **data):
    #     for key, value in data.items():
    #         if key in self.__fields_set__:
    #             continue
    #         if key not in self.__fields__:
    #             continue
    #         if value is None or value == 0:
    #             continue
    #         setattr(self, key, value)
