from datetime import datetime, date, time


class Date:
    """A class to represent a date.

    ### Attributes
    - **year** `int`: The year of the date.
    - **month** `int`: The month of the date.
    - **day** `int`: The day of the date.
    """

    def __init__(self, date: date):
        """Constructs all the necessary attributes for the date object.

        ### Parameters
        - **date** `date`: The date object from the **datetime** module.
        """
        self.year: int = date.year
        self.month: int = date.month
        self.day: int = date.day

    def __str__(self):
        """Returns the string representation of the date object.

        ### Returns
        - `str`: The string representation in the format `day/month/year`.
        """
        return f"{self.day}/{self.month}/{self.year}"


class Time:
    """A class to represent a time.

    ### Attributes
    - **hour** `int`: The hour of the time.
    - **minute** `int`: The minute of the time.
    - **second** `int`: The second of the time.
    """

    def __init__(self, time: time):
        """Constructs all the necessary attributes for the time object.

        ### Parameters
        - **time** `time`: The time object from the **datetime** module.
        """
        self.hour: int = time.hour
        self.minute: int = time.minute
        self.second: int = time.second

    def __str__(self):
        """Returns the string representation of the time object.

        ### Returns
        - `str`: The string representation in the format `hour:minute:second`.
        """
        return f"{self.hour}:{self.minute}:{self.second}"


class DateTime:
    """A class to represent a datetime.

    ### Attributes
    - **date** `Date`: The date part of the datetime.
    - **time** `Time`: The time part of the datetime.
    """

    def __init__(self, datetime: datetime):
        """Constructs all the necessary attributes for the datetime object.

        ### Parameters
        - **datetime** `datetime`: The datetime object from the **datetime** module.
        """
        self.date: Date = Date(datetime.date())
        self.time: Time = Time(datetime.time())

    def __str__(self):
        """Returns the string representation of the datetime object.

        ### Returns
        - `str`: The string representation in the format `day/month/year - hour:minute:second`.
        """
        return f"{str(self.date)} - {str(self.time)}"


__all__ = ["Date", "Time", "DateTime"]
