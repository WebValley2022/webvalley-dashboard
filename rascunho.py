#compare polution of pm10 in santa chiara
print("insert a starting day")
day1 = input()
print("insert a starting month")
month1 = input()
date_start = "2020-" +month1+ "-"+day1
print(date_start)

print("insert a ending day")
day2 = input()
print("insert a ending month")
month2 = input()
date_end = "2022-" +month2+ "-"+day2
print(date_end)

print("insert target concentration")
concen = input()

ds_gas_day = df[(df.Inquinante == "PM10") 
& (df.Data > date_start) & (df.Data < date_end) & (df.Valore == concen)] 

sns.barplot(y="Valore", x="Data", hue="Inquinante", data=ds_gas_day)
xticks(rotation = 90)