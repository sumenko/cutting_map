
import ezdxf
from ezdxf.enums import TextEntityAlignment

import json
from pprint import pprint
from math import ceil

class CutPrinter():
    def __init__(self, fname, global_scale=53, DEBUG=False):
        self.fname = fname
        self.doc = ezdxf.readfile('50.dxf')
        self.msp = self.doc.modelspace()
        self.page_y = 0
        self.global_scale = global_scale
        self.DEBUG = DEBUG
        self.page_width = 297
        self.page_height = 210
        self.page_x_space = 10
        self.page_y_space = 10
        self.beam_height = 200
        names = self.doc.layouts.names()
        names.remove('Model')
        current_lo = self.doc.layouts.new('New')
        for name in names:
            self.doc.layouts.delete(name)

        self.page_top_offset = 10
        self.page_bottom_offset = 10
        self.block_height = 20
        self.blocks_per_page = int((self.page_height - (self.page_top_offset + self.page_bottom_offset)) /
                                   (self.block_height))


    def save(self):
        try:
            self.doc.saveas(self.fname)
        except PermissionError as p:
            print(p)

    
    def add_rect(self, x, y, w, h, explode=False, attrs=None):
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
                self.msp.add_line(p1, p2, dxfattribs=attrs)


    def print_task(self, solution, taskName):
        """ Prints all pages of the solution """
        page_x = 0
        pages_num = ceil((len(solution) * self.block_height) /
                     (self.page_height - (self.page_bottom_offset + self.page_top_offset)))

        for page in range(pages_num):
            start_detail = page * self.blocks_per_page
            end_detail = min((page + 1) * self.blocks_per_page - 1, len(solution))
            details = solution[start_detail:end_detail]
            title = f'{taskName} {page+1} / {pages_num}'
            point = (page_x, self.page_y)
            self.print_task_page(point, title, details)
    
            page_x += (self.page_width + self.page_x_space) * self.global_scale
        self.page_y += (self.page_height + self.page_y_space) * self.global_scale
    
    def point(self, x, y):
        return (x * self.global_scale,
                y * self.global_scale)

    def print_task_page(self, point, title, details):
        """ Prints single solution page """
        cursor_x = point[0] + (25) * self.global_scale
        cursor_y = point[1] + (self.page_height - 15) * self.global_scale

        self.msp.add_blockref('SheetSmall', point, dxfattribs={
                                'xscale': self.global_scale,
                                'yscale': self.global_scale,
                                'rotation': 0
                                })
        self.msp.add_text(
                 title,
                 height=5*self.global_scale,
                 ).set_placement(
                 (cursor_x, cursor_y),
                 align=TextEntityAlignment.BOTTOM_LEFT)
        
        for detail in details:
            cursor_y -= self.block_height * self.global_scale
            self.print_single_detail((cursor_x, cursor_y), detail)
    def c(self, l):
        return l * self.global_scale

    def print_single_detail(self, point, detail):
        self.add_rect(point[0], point[1], detail[0], self.beam_height, attrs={'color': 1})
        cursor_x = point[0]
        cursor_y = point[1]
        dim_y_pos = cursor_y - self.c(7)

        for element in detail[1]:
            self.add_rect(cursor_x, cursor_y, element, self.beam_height, attrs={'color': 5})
            dim = self.msp.add_linear_dim(
                                          base=(cursor_x, dim_y_pos),  # location of the dimension line
                                          p1=(cursor_x, cursor_y),  # 1st measurement point
                                          p2=(cursor_x + element, cursor_y),  # 2nd measurement point
                                          dimstyle="GOST 50",  # default dimension style
                                          )
            dim.render()
            self.msp.add_text(
                              f'{cursor_x + element - point[0]}',
                              height=1.8*self.global_scale,
                              dxfattribs={'rotation': 90}
                              ).set_placement(
                              (cursor_x + element - self.c(.5) , dim_y_pos + self.c(.5)),
                              align=TextEntityAlignment.BOTTOM_LEFT)
            cursor_x += element


if __name__ == '__main__':
    cp = CutPrinter('out.dxf', DEBUG=True)
    with open('tasks.json', encoding='UTF-8') as ifile:
        j = json.load(ifile)
        for key in j.keys():
            task = j[key]
            cp.print_task(task['solution'], task['taskName'])
        cp.save()
 
