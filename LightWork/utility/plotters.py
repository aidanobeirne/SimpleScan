
from __future__ import division, print_function, unicode_literals, absolute_import
import numpy as np
import LightWork.utility.helper_functions as h
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
import traceback


try:
    from PyQt5 import QtWidgets
except Exception:
    traceback.print_exc()


class ShallowPlotter():
    """ Tool to plot 2D LightWork data (i.e. only one variable is scanned)

    """

    def __init__(self, *args, **kw):
        '''
        input arguments: 
        '''
        self.opt = {  # default options
            'spec_staggering':  0,  # amount to displace spectra by
            'legend_label':     'voltage',
            'hovering_range':    None,
            'title':            'title',  # plot title
            'xlabel':           'x',
            'ylabel':           'y',
            'ilabel':           'intensity [a.u.]',
            'cmap':             'inferno',
            'cmap_series':      None,
            'shading':          'gouraud',
            'cr_m':             3,
            'cr_thresholds':    [],
            'sc_e_min':         None,
            'sc_e_max':         None,
            'shift_value':      0,
            'change_x_units':   False,
            'vmin':             None,
            'vmax':             None,
            'display_specs':    [],  # for clicking spectra function
            'xyhoveri':         [0, 0],  # for on_move
            'verbose':          False
        }

        self._process_kw(*args, **kw)

        # Axes and Figures
        plt.ion()
        self.fig, self.axs = plt.subplots(2, 1)
        plt.xlabel(self.opt['xlabel'])
        self.axs[0].set_ylabel(self.opt['ylabel'])
        self.axs[1].set_ylabel(self.opt['ilabel'])
        self.axs[1].set_xlim((min(self.x), max(self.x)))
        self.axs[1].legend(prop={'size': 10})
        vmin = self.opt['vmin'] if self.opt['vmin'] is not None else np.min(
            self.data)
        vmax = self.opt['vmax'] if self.opt['vmax'] is not None else np.max(
            self.data)
        self.data = self.data.reshape(self.xx.shape)
        self.colormeshplot = self.axs[0].pcolormesh(
            self.xx, self.yy, self.data, vmin=vmin, vmax=vmax, cmap=self.opt['cmap'], shading=self.opt['shading'])
        # plt.colorbar(self.colormeshplot, ax=self.axs[0], pad=0.02)

        self.fig.suptitle(self.opt['title'], fontsize=35)
        self.lines = {}
        self.specs = {}
        self.legend_vals = {}
        self.shift_is_held = False
        self.u_is_held = False
        self.color_counter = 0
        # events
        self.cids = []
        self.cids.append(self.fig.canvas.mpl_connect(
            'button_press_event', self.onclick))
        self.cids.append(self.fig.canvas.mpl_connect(
            'key_press_event', self.on_key_press))
        self.cids.append(self.fig.canvas.mpl_connect(
            'key_release_event', self.on_key_release))

    def _process_kw(self, *args, **kw):
        '''
        process args and kwargs
        '''

        for key, value in kw.items():
            self.opt[key] = value

        # construct data
        if len(args) == 3:
            datavars = ['x', 'y', 'data']
            for i in range(len(args)):
                setattr(self, datavars[i], args[i])
        elif len(args) == 2:
            datavars = ['experiment', 'map_to_sorter']
            for i in range(len(args)):
                setattr(self, datavars[i], args[i])
            self.data = []
            self.y = []
            for scan in self.experiment['master_data'].values():
                try:
                    self.data.append(scan['data']['reflection contrast'])
                except KeyError:
                    try:
                        self.data.append(scan['data']['spec dark subtracted'])
                    except KeyError:
                        self.data.append(scan['data']['spec'])
                self.y.append(h.get_from_dict(scan, self.map_to_sorter))
                self.x = np.array(scan['data']['wavelengths'])

            self.data = np.array([s for _, s in sorted(zip(self.y, self.data))])
            # self.data = np.array(self.data)
            self.y = np.array(sorted(self.y))
            
        else:
            raise ValueError('Incorrect data type format')

        if self.opt['change_x_units']:
            self.x = 1240/self.x
        self.xx, self.yy = np.meshgrid(self.x, self.y)

        if self.opt['cmap_series'] is not None:
            colormap = getattr(cm, self.opt['cmap_series'])
            self.colors = colormap(np.linspace(0, 1, len(self.y)))
            if self.opt['camp_series_flip']:
                self.colors = self.colors[::-1]

        # cosmic ray removal
        if self.opt['cr_thresholds']:
            self.data = np.array(h.RemoveCosmicRaysRecursive(
                self.data, self.opt['cr_m'], self.opt['cr_thresholds']))
        # y axis shift
        if self.opt['sc_e_min'] is not None:
            self.data = np.array(h.shift_correction_range(spectra=self.data, energies=np.array(self.x),
                                                          e_min=self.opt['sc_e_min'], e_max=self.opt['sc_e_max'], shift_value=self.opt['shift_value']))

    def onclick(self, event):
        if self.shift_is_held:
            yidx = (abs(self.y - event.ydata)).argmin()
            yvalue = self.y[yidx]
            if self.opt['cmap_series'] is not None:
                color = self.colors[yidx]
            else:
                color = f'C{self.color_counter}'
            self.lines[yvalue] = self.axs[0].axhline(
                yvalue, alpha=0.35, color=color)
            self.specs[yvalue] = self.axs[1].plot(
                self.x, self.data[yidx, :] + self.color_counter * self.opt['spec_staggering'], label='{}={}'.format(self.opt['legend_label'], np.round(yvalue, 2)), color=color)
            self.axs[1].legend(prop={'size': 10})
            self.color_counter += 1

        elif self.u_is_held:
            yidx = (abs(self.y - event.ydata)).argmin()
            yvalue = self.y[yidx]
            current_legend_values = np.array(
                [float(key) for key in self.lines.keys()])
            current_legend_keys = list(self.lines.keys())
            key_to_remove = current_legend_keys[abs(
                current_legend_values - yvalue).argmin()]

            # delete spec and line
            s = self.specs[key_to_remove].pop(0)
            s.remove()
            del s
            self.lines[key_to_remove].remove()
            l = self.lines.pop(key_to_remove)
            del l

            self.axs[1].legend(prop={'size': 10})

        # recompute the ax.dataLim
        self.axs[1].relim()
        # update ax.viewLim using the new dataLim
        self.axs[1].autoscale_view()
        self.fig.canvas.draw()

    def on_key_press(self, event):
        if event.key == 'shift':
            self.shift_is_held = True
        if event.key == 'u':
            self.u_is_held = True

    def on_key_release(self, event):
        if event.key == 'shift':
            self.shift_is_held = False
        if event.key == 'u':
            self.u_is_held = False
