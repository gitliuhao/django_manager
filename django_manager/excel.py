from datetime import datetime, date
import xlwt

style_heading = xlwt.easyxf(
    """
    font:
        name Arial,
        colour_index white,
        bold on,
        height 225;
    align:
        wrap off,
        vert center,
        horiz center;
    pattern:
        pattern solid,
        fore-colour blue;
    borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
    """
)
style_body = xlwt.easyxf(
    """
    font:
        name 宋体,
        bold off,
        height 200;
    align:
        wrap on,
        vert center,
        horiz center;
    borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
    """
)


class DjangoExcelIO(object):
    def __init__(self, admin_view, request, queryset):
        self.queryset = queryset
        self.request = request
        self.model_class = queryset.model
        self.fields = self.model_class._meta.fields

    def response(self):
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_prd = wb.add_sheet('PRD')
        for field in self.fields:
            pass


def get_excel_io(response=None, head_list=None, body_2list=None):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet_prd = wb.add_sheet('PRD')

    style_heading = xlwt.easyxf(
        """
        font:
            name Arial,
            colour_index white,
            bold on,
            height 225;
        align:
            wrap off,
            vert center,
            horiz center;
        pattern:
            pattern solid,
            fore-colour blue;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        """
    )
    style_body = xlwt.easyxf(
        """
        font:
            name 宋体,
            bold off,
            height 200;
        align:
            wrap on,
            vert center,
            horiz center;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        """
    )
    style_green = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x11;")
    style_red = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x0A;")
    # fmts = [
    #     'M/D/YY', 'D-MMM-YY', 'D-MMM', 'MMM-YY', 'h:mm AM/PM',
    #     'h:mm:ss AM/PM', 'h:mm', 'h:mm:ss', 'M/D/YY h:mm',
    #     'mm:ss', '[h]:mm:ss', 'mm:ss.0',
    # ]
    # style_body.num_format_str = fmts[0]
    num = 0
    width_list = []
    list_num = 0

    # 写入头部的数据
    for head_value in head_list:
        width_list.append(len(str(head_value)))
        sheet_prd.write(list_num, num, head_value, style_heading)
        num += 1
    list_num += 1
    # 写入内容的数据
    if body_2list:
        for body_list in body_2list:
            num = 0
            for body_value in body_list:
                str_value = str(body_value)
                width = 10 if len(str_value) <= 10 else len(str_value[:40])
                index = body_list.index(body_value)
                if width > width_list[index]:
                    width_list[index] = width
                if isinstance(body_value, datetime):
                    width_list[index] = int(width / 2)
                    style_body.num_format_str = 'M/D/YY h:mm'
                    sheet_prd.write(list_num, num, str_value, style_body)
                else:
                    width_list[index] = int(width / 2)
                    style_body.num_format_str = '0'
                    sheet_prd.write(list_num, num, str_value, style_body)

                num += 1
            list_num += 1

    # 控制每个列的width
    num = 0
    for width in width_list:
        sheet_prd.col(num).width = (width+1) * 250 * 2
        num += 1

    # 将流写入新的域空间
    wb.save(response)

    return response


# map
def map_dict_to_value(_list):
    def dict_to_value(x):
        lt = [ x[l] for l in _list]
        return lt
    return dict_to_value


def map_objects_to_value(fields):
    def objects_to_value(obj):
        values = []
        for field in fields:
            field_name, field_type = field.name, field.__class__.__name__
            value = getattr(obj, field_name)
            if field_type in ['ForeignKey', 'OneToOneField']:
                values.append(value.__str__())
            # elif field_type == 'DateTimeField':
            #     values.append(value.strftime('%Y-%m-%d %H:%M:%S'))
            elif field_type == 'BooleanField':
                values.append('是' if value else '否')
            elif field_type == 'CharField':
                values.append(value if not field.choices else getattr(obj, 'get_{}_display'.format(field_name))())
            else:
                values.append(value)
        return values
    return objects_to_value