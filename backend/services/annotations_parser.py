
import regex

class AnnotationsParser:
    def __init__(self):
        self.pattern = regex.compile('^[@]([A-Z]{2}\\d{4})$')
    
    def get_unique_ids(self, annotations):
        if not annotations:
            return []
        unique_ids = []
        is_at = False
        at_coord = None

        def get_center(bbox):
            if not bbox or not bbox.vertices: return None
            xs = [v.x for v in bbox.vertices if hasattr(v, 'x')]
            ys = [v.y for v in bbox.vertices if hasattr(v, 'y')]
            return (sum(xs)/len(xs), sum(ys)/len(ys)) if xs and ys else None
        
        def get_area(bbox):
            if not bbox or not bbox.vertices: return 0.0
            vertices = [v for v in bbox.vertices if hasattr(v, 'x') and hasattr(v, 'y')]
            if len(vertices) < 3: return 0.0
            area = 0.0
            for i in range(len(vertices)):
                j = (i + 1) % len(vertices)
                area += vertices[i].x * vertices[j].y
                area -= vertices[j].x * vertices[i].y
            return abs(area) / 2.0

        for annotation in annotations:
            text = annotation.description
            coord = get_center(annotation.bounding_poly)
            area = get_area(annotation.bounding_poly)

            # print('->', text)

            # fix l → I and 1 → I
            if len(text)==6 and (text[1]=='l' or text[1]=='1'): text = text[0] + 'I' + text[2:]
            elif len(text)==7 and (text[2]=='l' or text[1]=='1'): text = text[:2] + 'I' + text[3:]


            # print('|--', text)

            if text == '@':
                is_at = True
                at_coord = coord
                continue

            if regex.match(self.pattern, text[:7]):   # normal IDs
                unique_ids.append((text[:7], coord))

            if is_at:  # case: '@' + text
                combined = '@' + text[:6]
                if regex.match(self.pattern, combined):
                    # pick average of @ and ID coordinate if both exist
                    if at_coord and coord:
                        coord = ((at_coord[0]+coord[0])/2, (at_coord[1]+coord[1])/2)
                    else:
                        coord = at_coord or coord
                    print("Combined:", combined)
                    print("Area:", area)
                    if area < 1000:
                        continue
                    # print('|->', combined)
                    unique_ids.append((combined, coord))
                is_at = False

        return unique_ids