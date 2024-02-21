from decimal import *
import numpy as np

from settings import Settings


class FoodSource:
    def __init__(
        self,
        params: list,
        index: int,
        affect_recruitment: bool = True,
        affect_pheromone_amount: bool = True,
    ):
        [x, y, radius, amount, quality, created_at_step, ends_at_step] = params
        self.id = index
        self.x = x
        self.y = y
        self.created_at = created_at_step
        self.ends_at = ends_at_step
        self.radius = Decimal(radius)
        self.initial_amount = int(amount)
        self.amount = int(amount)
        self.quality = Decimal(quality)

        self.affect_recruitment = affect_recruitment
        self.affect_pheromone_amount = affect_pheromone_amount

    def get_food_params(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": self.id,
            "radius": float(self.radius),
            "initial_amount": self.initial_amount,
            "amount": self.amount,
            "quality": float(self.quality),
            "created_at": self.created_at,
            "removed_at": self.ends_at,
        }

    def take_food(self):
        self.amount = self.amount - 1

    def find_food(self, x: Decimal, y: Decimal, step: int):
        if (
            self.created_at > step
            or (self.ends_at is not None and self.ends_at < step)
            or self.amount <= 0
        ):
            return False

        is_near = (
            np.linalg.norm(np.array([x, y]) - np.array([self.x, self.y])) < self.radius
        )
        if is_near:
            self.take_food()
            return True
        return False


class FoodSources:
    def __init__(self, settings: Settings):
        self.foods = []
        for index, food_params in enumerate(settings.FOOD_SOURCES):
            self.foods.append(
                FoodSource(
                    food_params,
                    index,
                    affect_recruitment=settings.AFFECT_RECRUITMENT,
                    affect_pheromone_amount=settings.AFFECT_PHEROMONE_AMOUNT,
                )
            )

    def find_food(self, x: Decimal, y: Decimal, step: int):
        for food in self.foods:
            if food.find_food(x, y, step):
                return food
        return None

    def get_food_data(self):
        result = []
        for food in self.foods:
            result.append(food.get_food_params())
        return result
