# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 12:05:37 2016

@author: Warner
"""

import simpy
import random
import pandas as pd
import numpy
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls

""" Input Variables """
simTime = 60 #Duration of the Simulation
riskPreference = [1,3] #Levels of Risk Aversion/Preference
riskLevel = [1,10] #value associated with person's likelihood to have accident
c = 101 #Number of customers in this insurance market
balance = 5000 # Insurance firm's starting balance
rs = 31 # Random Seed
""" Insurance cost every period """
cheapCost = 50
mediumCost = 100
expensiveCost = 200
accidentCost = 5000

""" Data Collection """
CUSTOMER_DATA = [] #Customer number, Riskiness, and Risk Preference
SIM_LOG = []

class Agency(object):
    def __init__(self, env, simTime):
        self.env = env
        self.simTime = simTime
        self.cheapReq = simpy.Resource(env)
        self.mediumReq = simpy.Resource(env)
        self.expensiveReq = simpy.Resource(env)
    
    def cheap(self, simTime):
        yield self.env.timeout(simTime)
    def medium(self, simTime):
        yield self.env.timeout(simTime)
    def expensive(self, simTime):
        yield self.env.timeout(simTime)
    
    
def Customer(env, simTime, number, riskPref, riskLevel, agency):
    
    preference = random.randint(*riskPref)
    riskiness = random.randint(*riskLevel)
    
    if preference == 3:
        with agency.cheapReq.request() as req:
            yield req
            CUSTOMER_DATA.append([number, riskiness, preference])
        while env.now <= simTime:
            payment = cheapCost
            if riskiness == 10:
                chance = random.randint(1,5)
                if chance == 1:
                        payment -= accidentCost
            SIM_LOG.append([env.now, number, payment])
            yield env.timeout(1)
                
    elif preference == 2:
        with agency.mediumReq.request() as req:
            yield req
            CUSTOMER_DATA.append([number, riskiness, preference])
        while env.now <= simTime:
            payment = mediumCost
            if riskiness == 10:
                chance = random.randint(1,5)
                if chance == 1:
                    payment -= accidentCost
            SIM_LOG.append([env.now, number, payment])
            yield env.timeout(1)
    
    else:
        with agency.expensiveReq.request() as req:
            yield req
            CUSTOMER_DATA.append([number, riskiness, preference])
        while env.now <= simTime:
            payment = expensiveCost
            if riskiness == 10:
                chance = random.randint(1,5)
                if chance == 1:
                    payment -= accidentCost
            SIM_LOG.append([env.now, number, payment])
            yield env.timeout(1)            

       
def Market(env, time):
    agency = Agency(env, time)
    
    for number in range(c)[1:c]:
        env.process(Customer(env, simTime, number, riskPreference, riskLevel, agency))
        yield env.timeout(0) #instantaneously have all customers in beginning
        number += 1

random.seed(rs)        
env = simpy.Environment()
env.process(Market(env, simTime))

env.run(until=simTime)
      
      
CUSTOMER_DATA = pd.DataFrame(CUSTOMER_DATA, columns=["custID","riskiness","preference"])

SIM_LOG = pd.DataFrame(SIM_LOG, columns=["time","custID","payment"])
t = SIM_LOG.pivot("time","custID") #To calculate accidents per period
SIM_LOG = SIM_LOG.pivot("time","custID")

""" Calculate accidents per period"""
t[t > 0] = 0
t[t < 0] = 1
accidents = t.sum(axis=1)

""" Calculate other columns """
SIM_LOG["sum"] = SIM_LOG.sum(axis=1)

SIM_LOG.iloc[[0], [100]] += balance
SIM_LOG["balance"] = SIM_LOG["sum"].cumsum() #numpy

SIM_LOG["time"] = range(0, len(SIM_LOG))

""" Interactive Plots """
### py.sign_in()

trace1 = go.Scatter(x=SIM_LOG["time"], y=SIM_LOG["balance"], 
                    name="Balance", yaxis="y2")
trace2 = go.Bar(x=SIM_LOG["time"], y=accidents, name="Customer Accidents")

data = [trace1, trace2]

layout = go.Layout(
    title="Healthcare Provider Balance Simulation",
    xaxis=dict(title='Time'),
    yaxis=dict(title="Customer Accidents"),
    yaxis2=dict(
        title="Balance",
        titlefont=dict(color="rgb(148, 103, 189)"),
        tickfont=dict(color="rgb(148, 103, 189)"),
        overlaying="y",
        side="right"))
        
        
figure1 = go.Figure(data=data, layout=layout)
plot_url = py.plot(figure1, filename='multiple-axes-double')