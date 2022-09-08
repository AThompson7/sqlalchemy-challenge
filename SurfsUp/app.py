from flask import Flask, jsonify

import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func




# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes\
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>(enter start date)<br/>"
        f"/api/v1.0/<start>(enter start date)/(enter end date)<end>"
        
        )
#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session= Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_list.append(prcp_dict)
        
    return jsonify(prcp_list)

#Station route
@ app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)
    results = session.query(Station.name, Station.station).all()
    session.close()
    station_data = list(np.ravel(results))

    
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_str = dt.datetime.strptime(most_recent_date[0], "%Y-%m-%d").date()
    one_year_back = dt.datetime.strptime(most_recent_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    active_stations = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    active_station_id = active_stations[0][0]

    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_back)\
        .filter(Measurement.station == active_station_id).all()
    session.close()

    tobs_list = list(np.ravel(temperature_data))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>") 
def start_date(start): 
    session = Session(engine) 
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all() 
    session.close() 
    
    
    start_list = [] 
    for min, max, avg in results: 
        start_dict = {} 
        start_dict["min temp"] = min 
        start_dict["max temp"] = max 
        start_dict["avg temp"] = avg 
        start_list.append(start_dict)
        
        
    return jsonify(start_list)
    

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all() 
    session.close()

    date_range_list = []
    for min, max, avg in results:
        date_range_dict = {'Start Date': start,
            'End Date': end}
        date_range_dict["min temp"] = min 
        date_range_dict["max temp"] = max 
        date_range_dict["avg temp"] = avg 
        date_range_list.append(date_range_dict)
    return jsonify(date_range_list)




if __name__ == '__main__':
    app.run(debug=True)




