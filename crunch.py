import csv
import datetime
import math
import os

"""
John Hopkins University COVID-19 Daily US Confirmed cases aggregator.

John Hopkins daily confirmed and dead are usually given by state, I personally rather see this information as a whole for the whole country.

This will add up all the numbers from each daily .csv and then print an output csv to stdout.

It will also calculate a confirmed cases K (acceleration) to plug into exponential or logistic functions on the last column.

Data has been obtained from Johns Hopkins University (JHU) Gitlab Repo
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
"""

COUNTRY=1
CONFIRMED=3
DEAD=4

class record:
  def __init__(self, date, month, day, year, confirmed, dead, k):
    self.date = date
    self.month = month
    self.day = day
    self.year = year
    self.confirmed = confirmed
    self.dead = dead
    self.k = k
  def __str__(self):
    return "{0},{1},{2},{3}".format(self.date,self.confirmed,self.dead,self.k)

def zero_pad(n):
  if n < 10:
      return '0' + str(n)
  return str(n)

def daily_numbers(month, date, year, country):
  '''Adds up the numbers from all the different counties, states as a US total'''
  confirmed=0
  dead=0
  file_name = 'data/' + zero_pad(month) + '-' + zero_pad(date) + '-' + zero_pad(year) + '.csv'
  if not os.path.exists(file_name):
    print("Warning: No data file for {0}-{1}-{2}".format(zero_pad(month), zero_pad(date), year))
    return (None,None)
  with open(file_name, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      if row[COUNTRY] == country:
        if row[CONFIRMED] == '':
          row[CONFIRMED] = 0
        if row[DEAD] == '':
          row[DEAD] = 0
        confirmed += int(row[CONFIRMED])
        dead += int(row[DEAD])
  return (confirmed, dead)

def monthly_numbers(results, month, country):
  global COUNTRY
  global CONFIRMED
  global DEAD
  start_day=1
  end_day=32
  if month == 1:
    start_day=22
  if month == 2:
    end_day = 30
  if month == 3:
    end_day = min(32, datetime.datetime.today().day+1)
  prev_dead = 0
  for day in range(start_day, end_day):
    if month >= 3 and day >= 22 and COUNTRY==1:
      # new fields were added on 03-23-2020
      COUNTRY=3
      CONFIRMED=7
      DEAD=8
    confirmed, dead =  daily_numbers(month, day, 2020, country)
    if confirmed == None and dead == None:
      continue
    k=0
    k_period=7
    if len(results) > k_period:
      last_record = results[-(k_period+1)]
      prev_dead = last_record.dead

    if confirmed > 0 and prev_dead > 0:
      k = math.log(dead/prev_dead)/k_period
      print("day={0} results[-8] -> prev_dead={1} dead={2} k={3} log({4}/{5})/7".format(day, prev_dead, dead, k, prev_dead, dead))

    r = record('{0}-{1}-2020'.format(zero_pad(month), zero_pad(day)), month, day, 2020, confirmed, dead, k) 
    results.append(r)

def crunch_country_report(country):
  confirmed = 0
  dead = 0
  results = []
  for month in range(2,4):
    monthly_numbers(results, month, country)
  filename = 'output_' + country + '.csv'
  with open(filename,'w') as output:
    output.write('Date,Confirmed,Dead,K\n')
    for r in results:
      output.write(str(r))
      output.write('\n')
  print('Done with ' + filename)

if __name__ == '__main__':
  countries=['US','Spain','Italy']
  for country in countries:
    COUNTRY=1
    CONFIRMED=3
    DEAD=4
    crunch_country_report(country)
