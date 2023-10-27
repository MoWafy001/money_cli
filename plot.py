import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# time range (start of this month to end of this month)
# Get the current date
now = datetime.datetime.now()

# Get the start of the current month
start_of_month = datetime.datetime(now.year, now.month, 1)
print(start_of_month)

# Get the end of the current month
next_month = start_of_month.replace(month=start_of_month.month+1, day=1)
end_of_month = next_month - datetime.timedelta(days=0)
print(end_of_month)

# Connect to the database
conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

# get history where date is between start_of_month and end_of_month
c.execute("SELECT * FROM history WHERE date BETWEEN ? AND ?", (start_of_month, end_of_month))
rows = c.fetchall()
print(len(rows))

# Close the database connection
conn.close()

# select only rows with negative values
rows = [row for row in rows if row[1] < 0]

# format all date to YYYY-MM-DD
rows = [((row[0].split(' '))[0], row[1]) for row in rows]

# group by date and add up all the values
r = {}
for row in rows:
    if row[0] in r:
        r[row[0]] += row[1]
    else:
        r[row[0]] = row[1]

# convert the dictionary back to a list of tuples
rows = [(key, value) for key, value in r.items()]
print(len(rows))

# plot the data in a bar chart
dates = [row[0] for row in rows]
values = [row[1] for row in rows]
print(rows)

# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# plot the bar chart in the first subplot
ax1.bar(dates, values)

# add a horizontal line for the average value
average = sum(values) / len(values)
ax1.axhline(y=average, color='r', linestyle='-')

# set the x-axis labels to be rotated 45 degrees
ax1.set_xticklabels(dates, rotation=45)

# set the title and axis labels
ax1.set_title('Expenses for the Month')
ax1.set_xlabel('Date')
ax1.set_ylabel('Amount')

# add text to each bar
for i, v in enumerate(values):
    ax1.text(i, v - 5, str(v), color='black', ha='center', fontweight='bold')

# add an accumulative sum line chart
cumulative_values = [sum(values[:i]) for i in range(1, len(values) + 1)]

# plot the cumulative sum line chart in the second subplot
ax2.plot(dates, cumulative_values, color='r', linestyle='-', marker='o', label='Cumulative')


# add text to each point in the second subplot
for i, v in enumerate(cumulative_values):
    ax2.text(i * 1.01, v * 1.01, str(v), color='black', ha='left')

# if the rows don't reach the end of the month, add projected values
# subtract one day from the end of the month
e = end_of_month - datetime.timedelta(days=1)
if rows[-1][0] != str(e).split(' ')[0]:
    # get the last value in the cumulative values list
    last_value = cumulative_values[-1]

    # get the number of days between the last date and the end of the month
    days = datetime.datetime.strptime(str(e).split(' ')[0], '%Y-%m-%d').day - datetime.datetime.strptime(rows[-1][0], '%Y-%m-%d').day
    print(days)

    # calculate the projected value by dividing the last value by the number of days in the month
    projected_value = last_value / len(rows)

    # add the projected values to the cumulative values list
    for i in range(days):
        cumulative_values.append(cumulative_values[-1] + projected_value)

    # add the projected values to the dates list
    for i in range(days):
        dates.append((datetime.datetime.strptime(rows[-1][0], '%Y-%m-%d') + datetime.timedelta(days=i+1)).strftime('%Y-%m-%d'))

    # only select the projected values
    cumulative_values = cumulative_values[-days-1:]

    # plot the projected values
    ax2.plot(dates[-days-1:], cumulative_values, color='g', linestyle='--', marker='o', label='Projected')

# set the title and axis labels
ax2.set_title('Cumulative Expenses for the Month')
# set the x-axis labels to be rotated 45 degrees
ax2.set_xticklabels(dates, rotation=45)
ax2.set_xlabel('Date')
ax2.set_ylabel('Amount')

# show the plot
plt.show()

print(sum(values))

