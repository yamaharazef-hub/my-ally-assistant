from plugin import plugin


@plugin("leap year")
def leap_year(ally, s):
    if s == "":
        s = ally.input("Enter a year: ")
    try:
        year = int(s)
    except ValueError:
        ally.say(
            "Wrong input. Please make sure you just enter an integer e.g. '2012'."
        )
        return
    else:
        if (
            (year % 400 == 0)
            and (year % 100 == 0)
            or (year % 4 == 0)
            and (year % 100 != 0)
        ):
            ally.say(f"{year} is a leap year.")
        else:
            ally.say(f"{year} is not a leap year.")
