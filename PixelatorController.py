import tango
from tango import AttrWriteType, DevState, DispLevel, AttrQuality
from tango.server import Device, attribute, command, device_property

class PixelatorController(Device):
     attr_dict = {
          0: {'atPositionCheckInterval': 0.002,
               'atPositionCheckTimeout': 10.0,
               'autoOffMode': 'Never',
               'axisName': 'APD Voltage',
               'beamlineControlPosition': 0,
               'coarsePositioner': '',
               'description': '',
               'distributionMode': 'nPlus1',
               'finePositioner': '',
               'hardwareUnitFactor': 22.625,
               'lowerSoftLimit': 0.0,
               'maxVelocity': 0.0,
               'name': 'APD Voltage',
               'positionOffset': -26.72,
               'unit': '(V)',
               'upperSoftLimit': 170.0,
               'velocityUnit': '(V/ms)'},
          # Rest of the attr_dict entries...
     }

     def init_device(self):
          super().init_device()

          def create_attributes(self):
               for index, attr_props in self.attr_dict.items():
                    attr_name = attr_props['name']
                    attr_info = tango.Attr(attr_name, tango.DevDouble, tango.AttrWriteType.READ_WRITE)
                    attr_info.set_disp_level(DispLevel.OPERATOR)
                    attr_info.set_unit(attr_props['unit'])
                    attr_info.set_standard_unit(attr_props['unit'])
                    attr_info.set_min_value(attr_props['lowerSoftLimit'])
                    attr_info.set_max_value(attr_props['upperSoftLimit'])
                    attr_info.set_writable(AttrWriteType.READ_WRITE)
                    attr_info.set_data_format("%6.2f")
                    attr_info.set_description(attr_props['description'])
                    attr_info.set_label(attr_props['name'])
                    attr_info.set_display_unit(attr_props['unit'])
                    attr_info.set_max_dim_x(1)
                    attr_info.set_max_dim_y(1)
                    attr_info.set_min_alarm(attr_props['lowerSoftLimit'])
                    attr_info.set_max_alarm(attr_props['upperSoftLimit'])
                    attr_info.set_min_warning(attr_props['lowerSoftLimit'])
                    attr_info.set_max_warning(attr_props['upperSoftLimit'])
                    attr_info.set_min_value_allowed(attr_props['lowerSoftLimit'])
                    attr_info.set_max_value_allowed(attr_props['upperSoftLimit'])
                    attr_info.set_abs_change(attr_props['hardwareUnitFactor'])
                    attr_info.set_rel_change(0.0)
                    attr_info.set_events(["change"])

                    self.add_attribute(attr_info, self.read_attr, None)

          def init_device(self):
               super().init_device()
               self.create_attributes()

          def read_attr(self, attr):
               index = int(attr.get_name().split('_')[-1])
               attr.set_value(self.attr_dict[index][attr.get_name()])

     def read_attr(self, attr):
          index = int(attr.get_name().split('_')[-1])
          attr.set_value(self.attr_dict[index][attr.get_name()])

if __name__ == "__main__":
     PixelatorController.run_server()

