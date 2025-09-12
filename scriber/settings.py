from dataclasses import dataclass


@dataclass
class Settings:
    currency_symbol: str = "$"
    decimal_separator: str = "."
    thousands_separator: str = ","
    number_decimals: int = 2
    percent_decimals: int = 1


def default_settings() -> Settings:
    return Settings()

