#!/usr/bin/micropython
# Mitosomat v1.0
# Copyright (C) 2021 KaratekHD
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
from time import sleep

from ev3dev2.motor import OUTPUT_A, OUTPUT_D, MoveTank, LargeMotor
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sound import Sound


class State:
    speed = 5
    unspeed = speed * -1
    time = 4

    def __init__(self, id, name, tank):
        self.id = id
        self.name = name
        self.tank = tank

    def run(self):
        raise Exception("Override this function!")

    def requires(self):
        return range(0, self.id)


class ProState(State):
    '''
    Spindelfasern bilden sich
    '''

    def __init__(self, tank):
        self.id = 0
        self.name = "Prophase"
        self.tank = tank

    def run(self):
        self.tank.on_for_seconds(
            right_speed=self.speed,
            left_speed=self.unspeed,
            seconds=self.time)


class MetaState(State):
    '''
    Spindelfasern docken an
    '''

    def __init__(self, tank):
        self.id = 1
        self.name = "Metaphase"
        self.tank = tank

    def run(self):
        sleep(2.5)


class AnaState(State):
    '''
    Chromosom wird auseinander gezogen
    '''

    def __init__(self, tank):
        self.id = 2
        self.name = "Anaphase"
        self.tank = tank

    def run(self):
        self.tank.on_for_seconds(
            right_speed=self.unspeed,
            left_speed=self.speed,
            seconds=self.time)


class StateMachine:
    current_state = -1

    def __init__(self, tank):
        self.tank = tank
        self.states = [
            ProState(
                self.tank), MetaState(
                self.tank), AnaState(
                self.tank)]

    def goto(self, state_id):
        if not state_id < len(self.states):
            raise Exception("Invalid state!")
        if self.current_state is not state_id - 1:
            for i in self.states[state_id].requires():
                self.states[i].run()
        self.current_state = state_id
        self.states[state_id].run()

    def full_simulation(self):
        for i in range(0, len(self.states)):
            self.states[i].run()


def main():
    # Schriftgröße auf 14 setzen
    os.system('setfont Lat15-TerminusBold14')
    tank = MoveTank(OUTPUT_A, OUTPUT_D)
    a = LargeMotor(OUTPUT_A)
    d = LargeMotor(OUTPUT_D)
    sm = StateMachine(tank)
    dummy = State(id=-9, name="Dummy", tank=None)
    speed = dummy.speed
    unspeed = dummy.unspeed
    print("Drücken Sie eine der Tasten auf der linken Seite der Fernbedienung, um die Simulation zu starten.")
    sound = Sound()
    sound.play_file('/home/robot/.sounds/ansage.wav')
    ir = InfraredSensor(INPUT_1)
    while True:
        try:
            if ir.top_left(channel=1) or ir.bottom_left(channel=1):
                sm.full_simulation()
            elif ir.top_left(channel=2):
                # D vorwärts
                d.on_for_seconds(seconds=0.5, speed=speed)
            elif ir.bottom_left(channel=2):
                # D rückwärts
                d.on_for_seconds(seconds=0.5, speed=unspeed)
            elif ir.top_right(channel=2):
                a.on_for_seconds(seconds=0.5, speed=unspeed)
            elif ir.bottom_right(channel=2):
                a.on_for_seconds(seconds=0.5, speed=speed)
            elif ir.bottom_left(channel=3) or ir.top_left(channel=3):
                sound.beep()
                sys.exit(0)
            elif ir.bottom_right(channel=3) or ir.top_right(channel=3):
                sound.beep()
                os.system("sudo shutdown now")
        except KeyboardInterrupt:
            break


main()
