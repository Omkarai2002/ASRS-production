import json

def build_result(image_name, records, detection):
    final_output = []

    output_template = {
        'IMG_NAME':              image_name, 
        'UNIQUE_ID':             None,  
        'QUANTITY':              None,  
        'VIN_NO':                None,  
        'EXCLUSION':             None
    }

    if not detection:
        output_template['EXCLUSION'] = "Empty Skid"
    elif detection and not records:
        output_template['EXCLUSION'] = "Sticker not found"
    elif len(records) > 1:
        output_template['EXCLUSION'] = "Multiple stickers detected"
    else:
        output_template['EXCLUSION'] = ""

    for record in records:
        tmp = output_template.copy()
        tmp['IMG_NAME'] = image_name
        
        if record:
            tmp['UNIQUE_ID'] = record[1]
            tmp['QUANTITY'] = 1
            tmp['VIN_NO'] = record[2]

        final_output.append(tmp)
    
    if not final_output:
        final_output.append(output_template)

    return final_output