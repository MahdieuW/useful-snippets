# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 17:14:33 2021

@author: Mahdieu
"""

import os
import datetime
import configparser
import numpy as np
import copy
from ast import literal_eval
import itertools
import csv
import pickle

from sys import stdout


def load_pickle(name):

    p.change_dir(name)
    loaded_obj = pickle.load( open( "{}.p".format(name), "rb" ) )
    p.return_last()
    return loaded_obj


def double_str(string):
    if isinstance(string, str):
        return str("\'" + string + "\'")
    else:
        return str(string)

def check_target(path):
    return not "." in path

def path_spider(path2check):
    """
    Funktion gibt alle Unterverzeichnisse in dem übergebenen Pfad zurück.
    """
    temp_path = os.getcwd()
    directorys = [(entry, os.path.join(path2check, entry)) for entry in os.listdir(path2check) if check_target(entry)]
    valids = []
    
    for target in directorys:
        valids += path_spider(os.path.join(path2check, target[1]))

    
    return directorys + valids
    
        
class path:

    """
    Objekte dieser Klasse beinhalten alle notwendigen Pfade und veranlassen einen Wechsel des working directory.

    Methoden:
        __init__: Methode intialisiert relative Pfade zu allen notwendigen Verzeichnissen.
        self.paths(path): Wechselt das Arbeitsverzeichnis in den zu dem übergebenen Schlüssel
                          im Dictionary self.paths korrespondierenden Pfad.
    """

    def __init__(self, height=1):

        self.temp_path = None #Variable um den ursprüngliche Pfad vor dem Wechsel zu speichern

        self.root = os.getcwd()
        root_directorys = os.listdir()[:-1]
        self.root_parent = os.path.dirname(self.root)
        for i in range(height-1):
            self.root_parent = os.path.dirname(self.root_parent)
       
        self.directorys = dict(path_spider(self.root_parent))
    
    def __getitem__(self, key):
        return self.directorys[key]

    def change_dir(self, path_name):
        """
        Wechselt das aktuelle Arbeitsverzeichnis in das über path_name übergebene Arbeitsverzeichnis.
        path_name muss Schlüssel des directorys dictionary sein.
        """
        
        self.temp_path = os.getcwd()
        try: 
            os.chdir(self.directorys[path_name])
        except:
            os.mkdir(self.directorys[path_name])
            os.chdir(self.directorys[path_name])


    def join2go(self, directory, target):
        """
        Wechselt das aktuelle Arbeitsverzeichnis in das in target übergebene Unterverzeichnis in dem Verzeichnis
        mit dem Schlüssel path_name aus path_names.
        """

        self.temp_path = os.getcwd()
        target = os.path.join(self.directorys[directory], target)
        try:
            os.chdir(target)
        except:             
            print("Warning: Had to make a new directory:\n         {}\n".format(target))
            os.mkdir(target)
            os.chdir(target)

    def return_last(self):
        """
        Methode wird genutzt, um in Verzeichnis aus dem der letzte Wechsel vollzogen wurde, zurückzukehren.
        """
        os.chdir(self.temp_path)
        self.temp_path = None

    def return_path(self, directory):

        return self.directorys[directory]
    
p = path()

    
class config:
    
    def __init__(self, filename="config", read=True):

        if filename[-4:] != ".ini":
            filename += ".ini"
        self.parser = configparser.ConfigParser()
        self.name = filename
        self.n_combinations = 0
        
        if read:
            p.change_dir("configs")
            self.parser.read(filename)
            p.return_last()
        
    def __getitem__(self, key):
        if isinstance(key, tuple):
            return literal_eval(self.parser[key[0]][key[1]])
        else:
            return literal_eval(self.parser[key])
    
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            self.parser[key[0]][key[1]] = double_str(value)
        else:
            self.parser[key]=double_str(value)
    
    def __nonzero__(self):
        return 1
    
    def listify(self):
        keys, values = ["setting"], ["values"]
        pairs = []
        for key in self.parser:
            pairs = pairs + [(key, item) for item in self.parser[key]]
        pairs = pairs[1:]
        for pair in pairs:
            keys.append(pair[1])
            values.append(self[pair])
        return [keys, values]
        
    def save(self, filename=None):
        p.change_dir("configs")
        if not filename: 
            filename = self.name
        else:
            if filename[-4:] != ".ini":
                filename += ".ini"
        
        with open(filename, 'w') as configfile:
                self.parser.write(configfile)
        p.return_last()
        
    def generator(self, args):
        
        distinct_values = []
        for key, args in args.items():
            values = []
            for arg in args:
                values.append((key, arg))
            distinct_values.append(values)

        combinations = list(itertools.product(*distinct_values))     
        self.n_combinations = len(combinations)
        for combination in combinations:
            
            for key, arg in combination:
                self[key] = arg
                
            yield (self, combination)

            

class table:
    
    def __init__(self, name, experiment_name=None):
        
        if not experiment_name:
            experiment_name = name
        self.experiment_name = experiment_name
        self.name = name
        self.table = [[]]
        self.current_X = len(self.table[0])
        self.current_Y = len(self.table)
        self.last_X = 0
        self.last_Y = 0
        self.track_X = 0
        self.track_Y = 0
        
        self.horizontal = None
        
    def update_X(self):
        self.last_X = self.track_X + 4

    def update_Y(self):
        self.last_Y = self.track_Y + 4 
        
    def get_position(self, orientation):
        if isinstance(orientation, str):

            if orientation == "right":
                self.horizontal = True
                self.update_X()                
                return (self.last_X, self.last_Y)
            elif orientation == "down":
                if self.horizontal:
                    self.reset_left()
                self.horizontal = False
                self.update_Y()
                return (self.last_X, self.last_Y)
            else:
                raise Exception("Orientation is not implemented!")
        else:
            self.last_X = orientation[0]
            self.last_Y = orientation[1]
            return orientation
        
    def reset_left(self):
        self.last_X = 1
        self.track_X = 1
        self.last_Y += 4
        
    def check_dims(self, coordinates):
        #x nach rechts weg
        #y nach unten
        x,y = coordinates
        if self.current_X <= x:
            for row in self.table:
                while len(row) <= x:
                    row.append("")

            self.current_X = len(self.table[0])
            
        if self.current_Y <= y:
            while len(self.table) <= y:
                self.table.append(["" for i in range(self.current_X)])

            self.current_Y = len(self.table)
            
    def check_conflict(self, entry, coordinates):
        current_entry = self.table[coordinates[1]][coordinates[0]]
        if current_entry != "" and current_entry != entry:
            print('Warning! Found the entry "{}" at ({},{})'.format(current_entry, coordinates[0], coordinates[1]))
            print('when trying write the entry "{}"!'.format(entry))
            return False
        else:
            return True
        
    def write_entry(self, entry, coordinates=(0,0), toplevel=True):
        if toplevel:
            coordinates = self.get_position(coordinates)
        self.check_dims(coordinates)
        if self.check_conflict(entry, coordinates):
            if isinstance(entry, float) or isinstance(entry, np.float32):
                entry = str(entry).replace(".", ",")
            self.table[coordinates[1]-1][coordinates[0]-1] = str(entry)
            self.track_X = coordinates[0]
            if coordinates[1] > self.track_Y:
                self.track_Y = coordinates[1]

            # self.update_x = True
            # self.update_Y = True

            
    def write_column(self, column, coordinates=(0,0), toplevel=True, shift_y=True):
        if toplevel:
            coordinates = self.get_position(coordinates)
        x = coordinates[0]
        if shift_y:
            column.insert(1, "")

        for index, value in enumerate(column):
            y_pos = coordinates[1] + index
            self.write_entry(value, 
                             (x, y_pos),
                             toplevel=False)
            
        return (x, y_pos)
    
    def write_table(self, sheet, coordinates=(1,1), index=None, title="", toplevel=True, shift_x=True):
        if toplevel:
            coordinates = self.get_position(coordinates)
        x, y = coordinates
        
        self.write_entry(title, (x,y))
        if toplevel:
            coordinates = self.get_position(coordinates)
        if shift_x:
            y += 1
        
        if isinstance(sheet, dict):
            columns = []
            for key, value in sheet.items():
                try:
                    columns.append([key] + list(value))
                except:
                    columns.append([key] + [value])
            sheet = columns
        length = []
        for col in sheet:
            try: length.append(len(col))
            except:
                length.append(1)
                
        length = range( max([len(col) for col in sheet]) -1)
        
        if not index:
            index = [i+1 for i in length]
        index = ["index"] + index
        empties = ["" for i in length]            
        sheet.insert(0, index)
        sheet.insert(1, empties)

        
        for index, column in enumerate(sheet):
            offset = self.write_column(column, 
                                       (x+index, y),
                                       toplevel=False)

        return offset
        
    def save_csv(self):
        p.change_dir(self.experiment_name)
        with open('{}.csv'.format(self.name), "w+", newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';',
                            quotechar=' ', quoting=csv.QUOTE_MINIMAL)
            for row in self.table:
                csv_writer.writerow(row)
        p.return_last()
        
    def save_pickle(self):
        p.change_dir(self.experiment_name)
        pickle.dump(self, open( "{}.p".format(self.name), "wb" ) )
        p.return_last()
        
    
class printer():
    
    def __init__(self):
        pass
    def new_line(self, item, border=(1,1)):
        writeout = "".join(["\n" for i in range(border[0])])
        writeout+= "{}".format(item)
        writeout += "".join(["\n" for i in range(border[1])])
        print(writeout)
    
    def title(self, item, border=(1,1)):
        
        to_print = "{}".format(item)
        length = int ( (80 - len(to_print))/2 ) 

        
        writeout = "".join(["\n" for i in range(border[0])])
        writeout += "-" * length
        writeout += to_print
        writeout += "-" * length
        writeout += "".join(["\n" for i in range(border[1])])
        print(writeout)
        
c = printer()

