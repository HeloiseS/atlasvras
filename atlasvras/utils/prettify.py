"""
:Description: This module contains some dictionaries and functions to prettify the VRA plots
:Creation Date: 2024-11-14
:Last Update: 2024-11-14
"""

vra_colors = {'white': '#F4F5F4',
               'blue': '#1F62FF',
               'yellow': '#FCD022',
               'orange':'#F06542',
               'red': '#D5202C'
               }


label_to_color = {'garbage':vra_colors['red'],
                 'good':vra_colors['blue'],
                 'pm':vra_colors['orange'],
                 'galactic':vra_colors['yellow'],
                 'auto-garbage':'grey',
                 'possible': vra_colors['white'],
                 None:'k'
                }
