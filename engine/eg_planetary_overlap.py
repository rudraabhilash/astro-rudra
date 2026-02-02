from planetary_overlap import compute_overlap

planets = {
    "Ketu": "Capricorn",
    "Jupiter": "Capricorn",
    "Venus": "Capricorn",
    "Saturn": "Scorpio",
    "Mars": "Sagittarius",
    "Sun": "Aquarius",
    "Mercury": "Aquarius",
    "Moon": "Pisces"
}

result = compute_overlap(planets, year=1926)
print(result)
if result:
    print("Overlap window (IST):")
    print("Start:", result[0])
    print("End:  ", result[1])
else:
    print("No continuous overlap")
