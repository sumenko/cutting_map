import ezdxf

class DXF_file:
    def __init__(self):
        # self.doc = ezdxf.new()
        self.doc = ezdxf.readfile('template.dxf')
        names = self.doc.layouts.names()
        names.remove('Model')
        self.msp = self.doc.modelspace()
        self.page_Y = 0  # при добавлении листа - прибавить его высоту
        # create new layout - current_lo
        current_lo = self.doc.layouts.new('New')
        for name in names:
            self.doc.layouts.delete(name)
    
        current_lo.page_setup(
            size=(297,210), margins = (0,0,0,0), units='mm',
            offset=(0,0), rotation=0, scale=16,name='A4',
            device='DWG to PDF.pc3')
        current_lo.add_viewport(
            center=(297/2,210/2), size=(297,210),
            view_center_point=(0,0), view_height=210)
        
        self.doc.layouts.set_active_layout('New')

        self.add_rect(0, 0, 297, 210, attrs={'color': 1})
        self.add_rect(297, 210, 297, 210, attrs={'color': 2})
        self.add_rect(0, 210, 297, 210)
        
        point = (1000, 1000)
        
        self.msp.add_blockref('SheetSmall', point, dxfattribs={
            'xscale': 53,
            'yscale': 53,
            'rotation': 0
        })
        current_lo.add_blockref('StampWatermark', (0,0), dxfattribs={
            'xscale': 1,
            'yscale': 1,
            'rotation': 0
        })


    def add_rect(self, x, y, w, h, explode=False, attrs=None):
        print(attrs)
        if attrs == None:
            attrs = {'color': 7}
        points = (
            (x    , y    ), (x + w, y    ),
            (x + w, y    ), (x + w, y + h),
            (x + w, y + h), (x, y + h    ),
        )
        if not explode:
            self.msp.add_lwpolyline(points=points, format='xy', close=True, dxfattribs=attrs)
        else:
            for p1, p2 in points:
                self.msp.add_line((p1[0], p1[1]), (p2[0], p2[1]), dxfattribs=attrs)


    def saveas(self, filename):
        self.doc.saveas(filename)


if __name__ == "__main__":
    dxf = DXF_file()
    dxf.saveas('test.dxf')


