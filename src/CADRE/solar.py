''' Solar discipline for CADRE '''

import os
from six.moves import range
import numpy as np

from openmdao.core.component import Component

from CADRE.kinematics import fixangles
import InterpolationLibrary

# Allow non-standard variable names for scientific calc
# pylint: disable-msg=C0103


class Solar_ExposedArea(Component):
    """Exposed area calculation for a given solar cell

    p: panel ID [0,11]
    c: cell ID [0,6]
    a: fin angle [0,90]
    z: azimuth [0,360]
    e: elevation [0,180]
    LOS: line of sight with the sun [0,1]
    """


    def __init__(self, n, raw1=None, raw2=None):
        super(Solar_ExposedArea, self).__init__()

        if raw1 is None:
            fpath = os.path.dirname(os.path.realpath(__file__))
            raw1 = np.genfromtxt(fpath + '/data/Solar/Area10.txt')
        if raw2 is None:
            fpath = os.path.dirname(os.path.realpath(__file__))
            raw2 = np.loadtxt(fpath + "/data/Solar/Area_all.txt")

        self.n = n
        self.nc = 7
        self.np = 12

        # Inputs
        self.add_param('finAngle', 0.0, units="rad",
                       desc="Fin angle of solar panel")

        self.add_param('azimuth', np.zeros((n, )), units='rad',
                       desc="Azimuth angle of the sun in the body-fixed frame "
                       "over time")

        self.add_param('elevation', np.zeros((n, )), units='rad',
                       desc='Elevation angle of the sun in the body-fixed '
                       'frame over time')

        # Outputs
        self.add_output('exposedArea', np.zeros((self.nc, self.np, self.n)),
                        desc="Exposed area to sun for each solar cell over time",
                        units='m**2', low=-5e-3, high=1.834e-1)

        self.na = 10
        self.nz = 73
        self.ne = 37
        angle = np.zeros(self.na)
        azimuth = np.zeros(self.nz)
        elevation = np.zeros(self.ne)

        xlimits = np.array([
            [0.0, np.pi/2.0],
            [0., np.pi*2.0],
            [0, np.pi]
        ])

        index = 0
        for i in range(self.na):
            angle[i] = raw1[index]
            index += 1
        for i in range(self.nz):
            azimuth[i] = raw1[index]
            index += 1

        index -= 1
        azimuth[self.nz - 1] = 2.0 * np.pi
        for i in range(self.ne):
            elevation[i] = raw1[index]
            index += 1

        angle[0] = 0.0
        angle[-1] = np.pi / 2.0
        azimuth[0] = 0.0
        azimuth[-1] = 2 * np.pi
        elevation[0] = 0.0
        elevation[-1] = np.pi

        xt = np.zeros((self.na * self.nz * self.ne, 3))

        counter = 0

        for a in range(self.na):
            for z in range(self.nz):
                for e in range(self.ne):
                    xt[counter, 0] = angle[a]
                    xt[counter, 1] = azimuth[z]
                    xt[counter, 2] = elevation[e]
                    counter += 1

        counter=0

        yt = np.zeros((self.na * self.nz * self.ne , self.np * self.nc))
        flat_size = self.na * self.nz * self.ne
        for p in range(self.np):
            for c in range(self.nc):
                yt[:, counter] = raw2[7 * p + c][119:119 + flat_size].reshape(flat_size)
                counter += 1

        self.MIME = InterpolationLibrary.EMTPS({
            'xlimits': xlimits,
            'num elems': [5, 5, 5],
            'wt fit': 1e5
        }, {
        }, {
        })

        self.MIME.add_training_pts('approx', xt, yt)
        self.MIME.setup()

        self.x = np.zeros((self.n, 3))
        self.Jfin = None
        self.Jaz = None
        self.Jel = None

    def solve_nonlinear(self, params, unknowns, resids):
        """ Calculate output. """

        self.setx(params)
        P = self.MIME.evaluate(self.x).T
        unknowns['exposedArea'] = P.reshape(7, 12, self.n, order='F')

    def setx(self, params):
        """ Sets our state array"""

        result = fixangles(self.n, params['azimuth'], params['elevation'])
        self.x[:, 0] = params['finAngle']
        self.x[:, 1] = result[0]
        self.x[:, 2] = result[1]

    def jacobian(self, params, unknowns, resids):
        """ Calculate and save derivatives. (i.e., Jacobian) """

        self.Jfin = self.MIME.evaluate(self.x, 0).reshape(self.n, 7, 12,
                                                         order='F')
        self.Jaz = self.MIME.evaluate(self.x, 1).reshape(self.n, 7, 12,
                                                        order='F')
        self.Jel = self.MIME.evaluate(self.x, 2).reshape(self.n, 7, 12,
                                                        order='F')

    def apply_linear(self, params, unknowns, dparams, dunknowns, dresids, mode):
        """ Matrix-vector product with the Jacobian. """

        deA = dresids['exposedArea']

        if mode == 'fwd':
            for c in range(7):

                if 'finAngle' in dparams:
                    deA[c, :, :] += \
                        self.Jfin[:, c, :].T * dparams['finAngle']

                if 'azimuth' in dparams:
                    deA[c, :, :] += \
                        self.Jaz[:, c, :].T * dparams['azimuth']

                if 'elevation' in dparams:
                    deA[c, :, :] += \
                        self.Jel[:, c, :].T * dparams['elevation']

        else:
            for c in range(7):

                # incoming arg is often sparse, so check it first
                if len(np.nonzero(dresids['exposedArea'][c, :, :])[0]) == 0:
                    continue

                if 'finAngle' in dparams:
                    dparams['finAngle'] += \
                        np.sum(
                            self.Jfin[:, c, :].T * deA[c, :, :])

                if 'azimuth' in dparams:
                    dparams['azimuth'] += \
                        np.sum(
                            self.Jaz[:, c, :].T * deA[c, :, :], 0)

                if 'elevation' in dparams:
                    dparams['elevation'] += \
                        np.sum(
                            self.Jel[:, c, :].T * deA[c, :, :], 0)
