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

    if not records:
        if not detection:
            output_template['EXCLUSION'] = "Empty Skid"
        elif detection:
            output_template['EXCLUSION'] = "Sticker not found"
        # elif len(records) > 1:
        #     output_template['EXCLUSION'] = "Multiple stickers detected"
    else:
        output_template['EXCLUSION'] = ""

    for record in records:
        tmp = output_template.copy()
        tmp['IMG_NAME'] = image_name
        
        if record:
            # record is a tuple: (unique_id, text_block)
            # record[0] = unique_id
            # record[1] = text_block (full text where ID was found)
            tmp['UNIQUE_ID'] = record.unique_id
            tmp['QUANTITY'] = 1
            # VIN_NO is not extracted yet - set to empty for now
            tmp['VIN_NO'] = record.vin_no

        final_output.append(tmp)
        break # take the first entry only
    
    if not final_output:
        final_output.append(output_template)

    return final_output