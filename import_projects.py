"""Import every project folder from the Desktop archive into the site.

Reads  C:\\Users\\Hamdy\\Desktop\\Oprell Projects\\<FOLDER>\\<SUBFOLDER(s)>\\<files>
Writes assets/proj/<slug>/<section-slug>/<file>.webp (+ -800.webp thumbs)
Copies videos / RAW files / PDFs as-is so nothing is lost.
Emits  projects_new.py  consumed by build.py:
    SECTIONS        - slug -> [ {name, images[], videos[], raw[], docs[]} ]
    EXTRA_PROJECTS  - PROJECTS-style dicts for folders not already on the site
    INDEX_CARDS     - (slug, title, meta, cover_stem) for the projects index

Run:  python import_projects.py
"""
import os
import re
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

SRC = Path(r'C:\Users\Hamdy\Desktop\Oprell Projects')
DST = Path('assets/proj')
OUT_PY = Path('projects_new.py')

IMG_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
RAW_EXT = {'.dng', '.cr3'}
VID_EXT = {'.mp4', '.mov'}
DOC_EXT = {'.pdf', '.xmp'}

# folder name -> (slug, mode)  mode 'merge' = attach sections to existing page
FOLDERS = [
    ('BELLA ROSE',                          'bella-rose',                          'new'),
    ('BROTHER',                             'brother',                             'skip'),
    ('CFO OFFICE',                          'cfo-office',                          'merge'),
    ('DUBAI HILLS',                         'dubai-hills',                         'new'),
    ('GINA VILLA',                          'gina-villa',                          'new'),
    ('GMI WASHROOM',                        'gmi-washroom',                        'new'),
    ('HESMAH VILLA',                        'hesmah-villa',                        'new'),
    ('HR OFFICE',                           'hr-office',                           'merge'),
    ('JAFZA WASHROOM',                      'jafza-washroom',                      'new'),
    ('JLT, HANFINIA WASHROOM',              'jlt-washroom',                        'merge'),
    ('JUMEIRAH BAY',                        'jumeirah-bay',                        'new'),
    ('JUMEIRAH GOLF ESTATE VILLA 48',       'jumeirah-golf-estate-villa-48',       'new'),
    ('JUMEIRAH PALM',                       'jumeirah-palm',                       'new'),
    ('JUMEIRAH VILLA 11',                   'jumeirah-villa-11',                   'new'),
    ('LANDSCAPE',                           'landscape',                           'merge'),
    ('MAEEN VILLA 165, THE LAKES',          'maeen-villa-165-the-lakes',           'new'),
    ('MEADOWS 2',                           'meadows-2',                           'new'),
    ('OFFICE PROJECT (NOT SURE)',           'office-project',                      'new'),
    ('PETA, MIRADOR LA COLECCION',          'peta-mirador-la-coleccion',           'new'),
    ('SUSAN BAKERY CO',                     'susans-baking',                       'merge'),
    ('VILLA 05, ARABIAN RANCHES',           'villa-05-arabian-ranches',            'new'),
    ('VILLA 08, ARABIAN RANCHES',           'villa-08-arabian-ranches',            'new'),
    ('VILLA 09, ARABIAN RANCHES PAINT WORK','villa-09-arabian-ranches-paint-work', 'new'),
    ('VILLA 15, SAHEEL, ARABIAN RANCHES',   'villa-15-saheel-arabian-ranches',     'new'),
    ('VILLA 248, SAHEEL, ARABIAN RANCHES',  'villa-248-saheel-arabian-ranches',    'new'),
    ('VILLA 49, ARABIAN RANCHES',           'villa-49-arabian-ranches',            'new'),
    ('VILLA 798, MBR CITY, DISTRICT ONE',   'villa-798-mbr-city-district-one',     'new'),
]

# source subfolders to skip entirely (slug -> dir names)
# HR OFFICE/HESMAH VILLA holds villa photos misfiled inside the office project —
# they already live in the hesmah-villa project.
SKIP_DIRS = {
    'hr-office': {'hesmah-villa'},
}

# display names for sections (slug, rel-dir-with-\\) -> title
# unlisted sections fall back to the last folder name, cleaned up.
SEC_NAME = {
    ('dubai-hills', r'LATEST FINISHED\FINISHED WITH LOGO'): 'Finished — with logo',
    ('jlt-washroom', 'NO LOGO'): 'Final — no logo',
    ('villa-08-arabian-ranches', r'HATTAN VILLA BEFORE\before with logo'):
        'Before — with logo',
    ('villa-09-arabian-ranches-paint-work',
     r'HATTAN VILLA 09 PAINTING SERVICE\HATTAN VILLA 09'): 'In progress',
    ('meadows-2', 'MEADOWS (BEFORE'): 'Before',
    ('meadows-2', 'MEADOWS AFTER'): 'After',
    ('villa-15-saheel-arabian-ranches', 'VILLA 15 BEFORE'): 'Before',
    ('villa-15-saheel-arabian-ranches', r'VILLA 15 BEFORE\VILLA 15 BEFORE'):
        'Before',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEE; VILLA 15 GF BEDROOM AREA 01'):
        'GF bedroom',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 2ND LIVING ROOM AREA'):
        'Second living room',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 DINING AREA'): 'Dining',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 ENTRANCE FOYER AREA'):
        'Entrance foyer',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 FF BEDROOM 3 AREA'):
        'FF bedroom 3',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 FIRST FLOOR FOYER AREA 02'):
        'FF foyer',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 KITCHEN AREA'): 'Kitchen',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 LANDSCAPE'): 'Landscape',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 LIVING ROOM AREA'):
        'Living room',
    ('villa-15-saheel-arabian-ranches',
     r'SAHEEL VILLA 15 NO LOGO\SAHEEL VILLA 15 MASTER BEDROOM AREA'):
        'Master bedroom',
    ('hr-office', 'HR OFFICE ENHANCE PHOTO'): 'Office — enhanced',
    ('jumeirah-golf-estate-villa-48',
     'JUMEIRAH GOLF ESTATE VILLA 48 (2025_04_17)'):
        'Site progress — April 2025',
    ('jumeirah-villa-11', 'VILLA 11 BEFORE(FROM ABDULLA)'):
        'Before — from Abdulla',
    ('jumeirah-villa-11', 'VILLA 11 JUMEIRAH ISLAND CLUSTER 31 (2025_04_25)'):
        'Finished — April 2025',
    ('villa-05-arabian-ranches', 'SAHEEL (26-06-23)'): 'June 2023',
    ('villa-05-arabian-ranches', 'SAHEEL VILLA 05 (FINISH)'): 'Finished',
    ('villa-248-saheel-arabian-ranches', 'SAHEEL VILLA 248 (EDITED)'):
        'Finished — edited',
    ('villa-248-saheel-arabian-ranches', 'SAHEEL VILLA 248 BEFORE (2024_08_30)'):
        'Before — August 2024',
    ('villa-49-arabian-ranches', 'ARABIAN RANCHES VILLA 49 (20-07-2025)'):
        'Finished — July 2025',
    ('villa-49-arabian-ranches', 'HATTAN VILLA 49 (2025_04_20)'):
        'Progress — April 2025',
    ('villa-49-arabian-ranches', 'VILLA 49 BEFORE'): 'Before',
    ('villa-49-arabian-ranches', 'VILLA 49 FIRST'): 'First visit',
    ('villa-798-mbr-city-district-one', 'MBR VILLA 798 (25-06-2025)'):
        'Progress — June 2025',
    ('maeen-villa-165-the-lakes', 'MAEEN LAKES BEFORE'): 'Before',
    ('maeen-villa-165-the-lakes', 'MAEEN LAKES VILLA 165 FINISH (EDITED)'):
        'Finished — edited',
    ('dubai-hills', 'DUBAI HILLS BEFORE'): 'Before',
    ('dubai-hills', 'LATEST FINISHED'): 'Finished — latest',
    ('dubai-hills', 'FINISHED'): 'Finished',
    ('villa-08-arabian-ranches', 'FINISHED PROJECT'): 'Finished',
    ('villa-08-arabian-ranches', 'HATTAN VILLA BEFORE'): 'Before',
    ('villa-08-arabian-ranches', 'HATTAN VILLA RENDERS'): 'Renders',
    ('villa-09-arabian-ranches-paint-work',
     'HATTAN VILLA 09 PAINTING SERVICE'): 'Painting service',
    ('jlt-washroom', 'JLT WASHROOM BEFORE'): 'Before',
    ('jafza-washroom', 'JAFZA WASHROOMS'): 'Jafza washrooms',
    ('gmi-washroom', 'GMI  WASHROOM'): 'GMI washroom',
    ('hesmah-villa', 'HESHAM VILLA'): 'Hesmah villa',
    ('jumeirah-golf-estate-villa-48', 'GOLF ESTATE'): 'Finished',
    ('jumeirah-palm', 'JUMEIRAH PALM'): 'Jumeirah Palm',
    ('landscape', 'LANDSCAPE'): 'Landscape',
    ('cfo-office', 'CFO OFFICE'): 'Office',
    ('cfo-office', r'CFO OFFICE\javsa office'): 'Javsa office',
    ('jumeirah-golf-estate-villa-48',
     'JUMEIRAH ISLAND VILLA 48(2025_05_28)'):
        'Site progress — May 2025',
    ('jumeirah-bay', 'JUMEIRAH BAY'): 'Jumeirah Bay',
    ('villa-798-mbr-city-district-one', 'FIRST PICTURE'): 'First pictures',
    ('villa-798-mbr-city-district-one', 'MBR VILLA 798'): 'Villa 798',
}

# Maeen room subfolders -> short titles
_MAEEN_ROOMS = {
    'villa-165-bedroom': 'Bedroom', 'villa-165-first-floor': 'First floor',
    'villa-165-kitchen': 'Kitchen', 'villa-165-landscape': 'Landscape',
    'villa-165-living-room': 'Living room', 'villa-165-livingroom': 'Living room',
    'villa-165-stairs': 'Stairs', 'villa-165-washroom': 'Washroom',
}

# source stems to exclude from the site (slug -> stems). Deleted photos.
SKIP = {
    'villa-798-mbr-city-district-one': {
        'img-3619', 'img-3758', 'img-3759', 'img-3760', 'img-3762',
        'img-3763', 'img-3769', 'img-3771', 'img-3772', 'img-3773',
        'img-3776', 'img-3781', 'img-3787',
        'img-3709', 'img-3710', 'img-3711', 'img-3717', 'img-3718',
        'img-3719', 'img-3720', 'img-3722'},
    'maeen-villa-165-the-lakes': {
        'maeen-lakes-villa-165-bedroom-0056'},
    'jumeirah-villa-11': {
        'whatsapp-image-2025-03-17-at-1-59-43-pm-1'},
}


# same-view duplicates removed (dHash dedupe pass)
_DUPES = {
    'cfo-office': {'cfo-office2', 'cfo-try', 'final-cfo-edited', 'final-cfo-edited-2', 'final-cfo-edited-3', 'final-cfo-edited1', 'image-6483441', 'image-6483441-1', 'img-1014', 'img-1015', 'img-1020', 'img-1021', 'javsa-office-1', 'javsa-office-2', 'javsa-office-4', 'javsa-office-5', 'profile-comp', 'profile-comp1', 'profile-comp2', 'testing-cfo'},
    'dubai-hills': {'bedroom-2-area-07-landscape', 'bedroom-3-area-08-landscape', 'bedroom-3-area-09-landscape', 'bedroom-3-area-10-landscape', 'bedroom-3-area-11-landscape', 'bedroom-3-area-12-landscape', 'bedroom-3-area-13-landscape', 'img-1835', 'img-1849', 'img-1868', 'img-1910', 'jacuzi-area-33-landscape', 'jacuzi-area-34-landscape', 'jacuzi-area-35-landscape', 'jacuzi-area-36-landscape', 'jacuzi-area-37-landscape', 'jacuzi-area-38-landscape', 'jacuzi-area-39-landscape', 'kitchen-area-19-landscape', 'livingroom-area-40-landscape', 'livingroom-area-41-landscape', 'livingroom-area-42-landscape', 'livingroom-area-43-landscape', 'livingroom-area-44-landscape', 'livingroom-area-45-landscape', 'livingroom-area-46-landscape', 'livingroom-sofa-1-area-51-landscape-editied', 'livingroom-sofa-1-area-51-landscape-editied-2', 'livingroom-sofa-1-area-51-landscape-enhance', 'pergola-area-23-landscape', 'pergola-area-31-landscape', 'pergola-area-32-landscape', 'sauna1-area-26-landscape', 'sauna1-area-27-landscape', 'sauna1-area-28-landscape', 'sauna1-area-29-landscape', 'sauna1-area-30-landscape', 'stair-greek-1-area-01-landscape-edited-lamp', 'stairs-area-01-landscape', 'stairs-area-02-landscape', 'stairs-area-03-landscape', 'stairs-area-04-landscape', 'stairs-area-16-landscape', 't-v-wall-area-16-landscape', 't-v-wall-area-17-landscape', 't-v-wall-area-18-landscape-with-lights', 't-v-wall-area-20-landscape', 'washroom-1-area-06-landscape', 'washroom-2-area-06-landscape', 'washroom-3-area-14-landscape', 'washroom-3-area-15-landscape', 'washroom-ground-1-area-26-landscape-texture', 'washroom1-ground-area-24-landscape'},
    'hesmah-villa': {'hesham-insta-05-with-logo'},
    'hr-office': {'hesham-insta-05-with-logo'},
    'jafza-washroom': {'jafza-post-01', 'jafza-post-02', 'jafza-post-03', 'whatsapp-image-2023-08-25-at-12-50-36-pm-4'},
    'jlt-washroom': {'img-1579-enhanced-nr', 'img-1579-enhanced-nr', 'img-1579-enhanced-nr-2', 'jlt-post-no-logo-01-edited', 'jlt-post-no-logo-02-edited', 'origsize-2', 'wc1', 'wc2'},
    'jumeirah-bay': {'image-67206145'},
    'jumeirah-golf-estate-villa-48': {'123123-0121', '123123-0128', '123123-0146', '123123-0150', '123123-0220', '123123-0253', '123123-0268', '123123-0293', '123123-0312', '12312312333336-1969', '12312312333336-1970', '12312312333336-1984', '12312312333336-1985', '12312312333336-1988', '12312312333336-1990', '12312312333336-1991', '12312312333336-1992', '12312312333336-1993', '12312312333336-1994', '12312312333336-1995', '12312312333336-1997', '12312312333336-1999', '12312312333336-2000', '12312312333336-2001', '12312312333336-2002', '12312312333336-2003', '12312312333336-2004', '12312312333336-2005', '12312312333336-2006', '12312312333336-2008', '12312312333336-2009', '12312312333336-2010', '12312312333336-2011', '12312312333336-2012', '12312312333336-2013', '12312312333336-2014', '12312312333336-2015', '12312312333336-2016', '12312312333336-2017', '12312312333336-2018', '12312312333336-2019', '12312312333336-2020', '12312312333336-2021', '12312312333336-2022', '12312312333336-2023', '12312312333336-2024', '12312312333336-2025', '12312312333336-2026', '12312312333336-2027', '12312312333336-2028', '12312312333336-2029', '12312312333336-2030', '12312312333336-2031', '12312312333336-2032', '12312312333336-2033', '12312312333336-2034', '12312312333336-2035', '12312312333336-2036', '12312312333336-2037', '12312312333336-2038', '12312312333336-2039', 'img-2228', 'img-2262', 'img-2310', 'img-2311'},
    'jumeirah-palm': {'jp-post-01', 'jp-post-02', 'jp-post-03', 'jp-post-04', 'jp-post-05', 'jp-post-06', 'jp-post-07', 'jp-post-08', 'jp-post-09', 'whatsapp-image-2023-08-17-at-2-06-51-pm', 'whatsapp-image-2023-08-17-at-2-08-45-pm-3', 'whatsapp-image-2023-08-17-at-2-09-23-pm', 'whatsapp-image-2023-08-17-at-2-09-23-pm-6', 'whatsapp-image-2023-08-17-at-2-09-23-pm-9'},
    'jumeirah-villa-11': {'12312312333336-0962', '12312312333336-0987', '12312312333336-0998', '12312312333336-1001', '12312312333336-1031', '12312312333336-1073', '12312312333336-1095', 'whatsapp-image-2025-03-17-at-2-07-50-pm'},
    'maeen-villa-165-the-lakes': {'document-name1', 'document-name1-16', 'document-name1-29', 'document-name1-31', 'document-name1-35', 'document-name1-37', 'document-name1-9', 'img-8480', 'maeen-lakes-mainentrance-3', 'maeen-lakes-villa-165-bedroom-0014', 'maeen-lakes-villa-165-bedroom-0015', 'maeen-lakes-villa-165-bedroom-0023', 'maeen-lakes-villa-165-bedroom-005', 'maeen-lakes-villa-165-bedroom-006', 'maeen-lakes-villa-165-firstfloor-0033', 'maeen-lakes-villa-165-landscape-001', 'maeen-lakes-villa-165-livingroom-0077-edited', 'maeen-lakes-villa-165-livingroom-0078-edited', 'maeen-lakes-villa-165-livingroom-0079-edited', 'maeen-lakes-villa-165-livingroom-0080-edited', 'maeen-lakes-villa-165-livingroom-0081-edited', 'maeen-lakes-villa-165-livingroom-0082-edited', 'maeen-lakes-villa-165-livingroom-0087', 'maeen-lakes-villa-165-livingroom-0091', 'maeen-lakes-villa-165-livingroom-0093'},
    'meadows-2': {'bedroom-new-3-area-22-landscape', 'entrancedoor-1-area-40-landscape-no-logo', 'golfroom-1-area-50-landscape-edited', 'livingroom-1-area-1-landscape-edited', 'meadows-2-kitchen-area', 'new-9', 'walkincloset-1-area-12-landscape'},
    'villa-05-arabian-ranches': {'img-3116', 'img-3117', 'img-3126', 'img-3132', 'img-3137', 'img-3187', 'img-3191', 'img-3209', 'img-3210', 'img-3214', 'img-3217', 'img-3235', 'img-3238', 'img-3244', 'img-3251', 'saheel-05-washroom-04-brightness-edit'},
    'villa-08-arabian-ranches': {'bbq-6', 'bbq-7', 'before-hattan-07', 'entrance-door-area-24-landscape', 'entrance-door-area-29-landscape-edited', 'fire-place-02-area-11-landscape', 'hattan-villa-new-01-area-01', 'hattan-villa-new-01-area-02', 'hattan-villa-new-01-area-03', 'hattan-villa-new-01-area-04', 'hattan-villa-new-01-area-09-1', 'hattan-villa-new-01-area-11', 'living-room-01-area-01-portrait', 'stair-1-area-26-landscape-high-contrast', 'whatsapp-image-2023-01-23-at-11-21-13-am', 'whatsapp-image-2023-08-24-at-11-27-57-pm', 'whatsapp-image-2023-08-24-at-11-27-57-pm-3'},
    'villa-09-arabian-ranches-paint-work': {'img-2424'},
    'villa-15-saheel-arabian-ranches': {'12312312333336-2517', '12312312333336-2524', '12312312333336-2525', '12312312333336-2526', '12312312333336-2538', '12312312333336-2542', '12312312333336-2554', '12312312333336-2562', '12312312333336-2567', 'saheel-villa-15-2nd-living-room-10-area-01', 'saheel-villa-15-dining-06-area-01', 'saheel-villa-15-dining-13-area-01', 'saheel-villa-15-dining-26-area-01', 'saheel-villa-15-dining-27-area-01', 'saheel-villa-15-entrance-foyer-05-area-01', 'saheel-villa-15-ff-bedroom-23-area-03', 'saheel-villa-15-ff-bedroom-24-area-03', 'saheel-villa-15-ff-bedroom-25-area-03', 'saheel-villa-15-first-floor-10-foyer-area-02', 'saheel-villa-15-first-floor-19-foyer-area-02', 'saheel-villa-15-gf-bedroom-07-area-01', 'saheel-villa-15-gf-bedroom-11-area-01', 'saheel-villa-15-gf-bedroom-16-area-01', 'saheel-villa-15-gf-bedroom-18-area-01', 'saheel-villa-15-gf-bedroom-21-area-01', 'saheel-villa-15-kitchen-03-area-01', 'saheel-villa-15-kitchen-14-area-01', 'saheel-villa-15-kitchen-19-area-01', 'saheel-villa-15-living-room-10-area', 'saheel-villa-15-living-room-16-area', 'saheel-villa-15-masterbedroom-12-area-02', 'saheel-villa-15-masterbedroom-21-area-02', 'saheel-villa-15-masterbedroom-26-area-02', 'saheel-villa-15-masterbedroom-33-area-02', 'whatsapp-image-2024-10-30-at-2-25-58-pm-1', 'whatsapp-image-2024-10-30-at-2-25-58-pm-2', 'whatsapp-image-2024-10-30-at-2-25-58-pm-3', 'whatsapp-image-2025-03-17-at-1-59-43-pm', 'whatsapp-image-2025-03-17-at-1-59-52-pm', 'whatsapp-image-2025-03-17-at-1-59-57-pm', 'whatsapp-image-2025-03-17-at-1-59-59-pm', 'whatsapp-image-2025-03-17-at-2-00-02-pm', 'whatsapp-image-2025-03-17-at-2-00-07-pm', 'whatsapp-image-2025-03-17-at-2-00-09-pm', 'whatsapp-image-2025-03-17-at-2-00-11-pm', 'whatsapp-image-2025-03-17-at-2-00-13-pm', 'whatsapp-image-2025-03-17-at-2-05-40-pm', 'whatsapp-image-2025-03-17-at-2-05-40-pm-1', 'whatsapp-image-2025-03-17-at-2-05-41-pm', 'whatsapp-image-2025-03-17-at-2-05-43-pm', 'whatsapp-image-2025-03-17-at-2-05-43-pm-1', 'whatsapp-image-2025-03-17-at-2-05-45-pm', 'whatsapp-image-2025-03-17-at-2-05-45-pm-1', 'whatsapp-image-2025-03-17-at-2-05-49-pm'},
    'villa-248-saheel-arabian-ranches': {'img-7264', 'img-7270', 'img-7279', 'img-7284', 'img-8348', 'saheel-248-living-room-07', 'saheel-villa-248-livingroom-0012-copy-w-skirting', 'saheel-villa-248-livingroom-0020', 'saheel-villa-248-livingroom-003'},
    'villa-49-arabian-ranches': {'1231231-0776', '1231231-0780', '1231231-0796', '1231231-0812', '1231231-0827', '1231231-0828', '1231231-0829', '1231231-0843', '1231231-0849', '1231231-0850', '1231231-0858', '1231231-0862', '1231231-0864', '1231231-0869', '1231231-0870', '1231231-0872', '1231231-0874', '1231231-0875', '1231231-0879', '1231231-0882', '1231231-0884', 'whatsapp-image-2024-06-19-at-8-55-45-pm-1', 'whatsapp-image-2024-07-05-at-3-55-47-pm', 'whatsapp-image-2024-07-05-at-3-55-53-pm', 'whatsapp-image-2024-07-05-at-3-56-27-pm-2', 'whatsapp-image-2025-07-16-at-11-52-45-am', 'whatsapp-image-2025-07-16-at-12-05-53-pm', 'whatsapp-image-2025-07-16-at-12-06-07-pm'},
    'villa-798-mbr-city-district-one': {'12312312333336-2860', '12312312333336-2868', '12312312333336-2900', '12312312333336-2920', '12312312333336-2923', '12312312333336-2931', '12312312333336-2933', '12312312333336-2935', '12312312333336-2962', '12312312333336-2965', '12312312333336-2967', '12312312333336-2987', '12312312333336-2990', '12312312333336-3053', '12312312333336-3057', '12312312333336-3091', '12312312333336-3101', '12312312333336-3102', '12312312333336-3108', '12312312333336-3112', '12312312333336-3115', '12312312333336-3118', '12312312333336-3119', '12312312333336-3135', '12312312333336-3150', '12312312333336-3164', '12312312333336-3165', '12312312333336-3223', '12312312333336-3229', '12312312333336-3231', '12312312333336-3240', '12312312333336-3245', '12312312333336-3257', '12312312333336-3262', '12312312333336-3263', '12312312333336-3264', '12312312333336-3277', '12312312333336-3278', '12312312333336-3287', '12312312333336-3288', '12312312333336-3294', '12312312333336-3362', '12312312333336-3377', '12312312333336-3386', 'img-3615', 'img-3618', 'img-3632', 'img-3637', 'img-3640', 'img-3645', 'img-3661', 'img-3664', 'img-3732'},
}
for _k, _v in _DUPES.items():
    SKIP.setdefault(_k, set()).update(_v)


# same-view duplicates - pass 2 (looser hash, visually verified)
_DUPES2 = {
    'cfo-office': {'cfo-office2-1'},
    'dubai-hills': {'img-1840', 'story-post-dubai-hills-01'},
    'gmi-washroom': {'gmi-6'},
    'jafza-washroom': {'91-update'},
    'jlt-washroom': {'57', 'whatsapp-image-2023-05-20-at-1-23-03-pm'},
    'jumeirah-golf-estate-villa-48': {'123123-0108', '123123-0157', '123123-0168', '123123-0176', '123123-0183', '123123-0195', '123123-0197', '123123-0207', '123123-0208', '123123-0216', '123123-0260', '123123-0261', '123123-0289', '12312312333336-2041', 'img-2221', 'img-2355', 'img-2358', 'img-2365'},
    'jumeirah-palm': {'whatsapp-image-2023-03-16-at-2-44-02-pm'},
    'jumeirah-villa-11': {'12312312333336-0935', '12312312333336-0939', '12312312333336-0970', '12312312333336-0974', '12312312333336-1002', '12312312333336-1003', '12312312333336-1006', '12312312333336-1023', '12312312333336-1026', '12312312333336-1034', '12312312333336-1036', '12312312333336-1038', '12312312333336-1045', '12312312333336-1049', '12312312333336-1057', '12312312333336-1064', '12312312333336-1078'},
    'maeen-villa-165-the-lakes': {'maeen-lakes-villa-165-bedroom-0024', 'maeen-lakes-villa-165-firstfloor-0041', 'maeen-lakes-villa-165-livingroom-0092', 'maeen-lakes-villa-165-stairs-004'},
    'meadows-2': {'img-2236'},
    'villa-05-arabian-ranches': {'img-3120', 'img-3124', 'img-3151', 'img-3170', 'img-3174', 'img-3194', 'img-3203'},
    'villa-09-arabian-ranches-paint-work': {'img-2422', 'img-2423'},
    'villa-15-saheel-arabian-ranches': {'12312312333336-2523', '12312312333336-2532', '12312312333336-2536', '12312312333336-2559', '12312312333336-2564', '12312312333336-2580', '333333333', '44444444', '55555555', 'saheel-villa-15-2nd-living-room-06-area-01', 'saheel-villa-15-dining-16-area-01', 'saheel-villa-15-dining-22-area-01', 'saheel-villa-15-entrance-foyer-02-area-01', 'saheel-villa-15-entrance-foyer-11-area-01', 'saheel-villa-15-first-floor-06-foyer-area-02', 'saheel-villa-15-gf-bedroom-19-area-01', 'saheel-villa-15-kitchen-29-area-01', 'saheel-villa-15-living-room-02-area', 'saheel-villa-15-masterbedroom-31-area-02'},
    'villa-248-saheel-arabian-ranches': {'img-7272', 'img-7274', 'img-7281', 'img-7287', 'saheel-villa-248-livingroom-001', 'saheel-villa-248-livingroom-002'},
    'villa-49-arabian-ranches': {'1231231-0815', '1231231-0821', '1231231-0823', '1231231-0846', '1231231-0851', '1231231-0860', '1231231-0880', 'whatsapp-image-2024-07-05-at-3-55-50-pm'},
    'villa-798-mbr-city-district-one': {'12312312333336-2862', '12312312333336-2863', '12312312333336-2908', '12312312333336-2915', '12312312333336-2950', '12312312333336-2981', '12312312333336-3068', '12312312333336-3086', '12312312333336-3093', '12312312333336-3117', '12312312333336-3185', '12312312333336-3194', '12312312333336-3200', '12312312333336-3201', '12312312333336-3216', '12312312333336-3220', '12312312333336-3239', '12312312333336-3243', '12312312333336-3253', '12312312333336-3255', '12312312333336-3258', '12312312333336-3260', '12312312333336-3267', '12312312333336-3275', '12312312333336-3284', '12312312333336-3293', '12312312333336-3326', '12312312333336-3345', '12312312333336-3384', 'img-3611', 'img-3636', 'img-3675', 'img-3708', 'img-3721', 'img-3740', 'img-3788', 'img-3793'},
}
for _k, _v in _DUPES2.items():
    SKIP.setdefault(_k, set()).update(_v)

# display metadata for brand-new project pages (title stays verbatim from folder)
META = {
    'bella-rose':                    ('Residential', 'Dubai'),
    'brother':                       ('Commercial', 'Dubai'),
    'dubai-hills':                   ('Residential', 'Dubai Hills, Dubai'),
    'gina-villa':                    ('Residential', 'Dubai'),
    'gmi-washroom':                  ('Renovation', 'Dubai'),
    'hesmah-villa':                  ('Residential', 'Dubai'),
    'jafza-washroom':                ('Renovation', 'Jafza, Dubai'),
    'jumeirah-bay':                  ('Residential', 'Jumeirah Bay, Dubai'),
    'jumeirah-golf-estate-villa-48': ('Residential', 'Jumeirah Golf Estates, Dubai'),
    'jumeirah-palm':                 ('Residential', 'Palm Jumeirah, Dubai'),
    'jumeirah-villa-11':             ('Residential', 'Jumeirah Islands, Dubai'),
    'maeen-villa-165-the-lakes':     ('Residential', 'Maeen, The Lakes, Dubai'),
    'meadows-2':                     ('Residential', 'Meadows 2, Dubai'),
    'office-project':                ('Commercial', 'Dubai'),
    'peta-mirador-la-coleccion':     ('Residential', 'Dubai'),
    'villa-05-arabian-ranches':      ('Residential', 'Arabian Ranches, Dubai'),
    'villa-08-arabian-ranches':      ('Residential', 'Hattan, Arabian Ranches, Dubai'),
    'villa-09-arabian-ranches-paint-work': ('Residential', 'Hattan, Arabian Ranches, Dubai'),
    'villa-15-saheel-arabian-ranches': ('Residential', 'Saheel, Arabian Ranches, Dubai'),
    'villa-248-saheel-arabian-ranches': ('Residential', 'Saheel, Arabian Ranches, Dubai'),
    'villa-49-arabian-ranches':      ('Residential', 'Hattan, Arabian Ranches, Dubai'),
    'villa-798-mbr-city-district-one': ('Residential', 'District One, MBR City, Dubai'),
}


def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-') or 'x'


def titleize(folder):
    t = folder.title()
    # keep acronyms tidy
    for a, b in (('Gmi', 'GMI'), ('Jafza', 'Jafza'), ('Jlt', 'JLT'),
                 ('Mbr', 'MBR'), ('Cfo', 'CFO'), ('Hr', 'HR')):
        t = re.sub(rf'\b{a}\b', b, t)
    return t


def make_webp(src, dst_stem):
    """dst_stem.webp (<=1600w) + dst_stem-800.webp. Returns (w_ok, err)."""
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = None
    try:
        im = ImageOps.exif_transpose(Image.open(src))
        if im.mode not in ('RGB', 'L'):
            im = im.convert('RGB')
        w, h = im.size
        mw = min(w, 1600)
        im2 = im.resize((mw, int(h * mw / w)), Image.LANCZOS) if mw < w else im
        im2.save(str(dst_stem) + '.webp', 'WEBP', quality=80, method=4)
        t800 = im.resize((min(w, 800), int(h * min(w, 800) / w)),
                         Image.LANCZOS) if w > 800 else im
        t800.save(str(dst_stem) + '-800.webp', 'WEBP', quality=80, method=4)
        return None
    except Exception as e:  # noqa: BLE001
        return f'{src}: {e}'


def _job(job):
    return make_webp(*job)


def rotated(src):
    """True if the source carries an EXIF orientation other than 1."""
    if Path(src).suffix.lower() not in ('.jpg', '.jpeg'):
        return False
    try:
        from PIL import Image
        return Image.open(src).getexif().get(274, 1) != 1
    except Exception:  # noqa: BLE001
        return False


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def probe_image(src):
    """True if PIL can open it (some 'RAW' files are renamed JPEG/MPO)."""
    try:
        from PIL import Image
        with Image.open(src) as im:
            return im.format in ('JPEG', 'MPO', 'PNG', 'WEBP')
    except Exception:  # noqa: BLE001
        return False


def scan():
    """Walk every folder -> jobs for conversion + section data."""
    jobs, sections, stats, used_stems = [], {}, {}, set()
    for folder, slug, mode in FOLDERS:
        fdir = SRC / folder
        secs = {}           # rel_dir -> section dict
        counts = dict(img=0, vid=0, raw=0, doc=0)
        skip_dirs = SKIP_DIRS.get(slug, ())
        for dirpath, _dirs, files in os.walk(fdir):
            _dirs[:] = [x for x in _dirs if slugify(x) not in skip_dirs]
            d = Path(dirpath)
            rel = d.relative_to(fdir)
            if (slug, str(rel)) in SEC_NAME:
                sec_name = SEC_NAME[(slug, str(rel))]
            elif str(rel) == '.':
                sec_name = folder
            elif slug == 'maeen-villa-165-the-lakes' and \
                    slugify(d.name) in _MAEEN_ROOMS:
                sec_name = _MAEEN_ROOMS[slugify(d.name)]
            else:
                sec_name = str(rel).replace('\\', ' / ')
                sec_name = (sec_name.split(' / ')[-1]
                            .replace('_', '-').replace('SAHEE;', 'SAHEEL'))
            sec_slug = slugify(str(rel)) if str(rel) != '.' else 'photos'
            outdir = DST / slug / sec_slug
            items = {'images': [], 'videos': [], 'raw': [], 'docs': []}
            for fn in sorted(files, key=natural_key):
                src = d / fn
                ext = src.suffix.lower()
                if slugify(src.stem) in SKIP.get(slug, ()):
                    continue
                if ext in IMG_EXT:
                    stem = slugify(src.stem)
                    outdir.mkdir(parents=True, exist_ok=True)
                    dst_stem = outdir / stem
                    n = 2
                    while str(dst_stem) in used_stems:
                        dst_stem = outdir / f'{stem}-{n}'
                        n += 1
                    used_stems.add(str(dst_stem))
                    jobs.append((str(src), str(dst_stem)))
                    items['images'].append(f'{slug}/{sec_slug}/{dst_stem.name}')
                    counts['img'] += 1
                elif ext in VID_EXT | RAW_EXT | DOC_EXT:
                    outdir.mkdir(parents=True, exist_ok=True)
                    nn = slugify(src.stem) + ext.replace('.cr3', '.cr3')
                    target = outdir / nn
                    relp = f'{slug}/{sec_slug}/{nn}'
                    if not target.exists():
                        target.write_bytes(src.read_bytes())
                    key = ('videos' if ext in VID_EXT else
                           'raw' if ext in RAW_EXT else 'docs')
                    # pseudo-RAWs that PIL can open get a real preview in the
                    # gallery instead of a bare download row
                    if ext in RAW_EXT and probe_image(src):
                        stem = slugify(src.stem) + '-raw'
                        dst_stem = outdir / stem
                        n = 2
                        while str(dst_stem) in used_stems:
                            dst_stem = outdir / f'{stem}-{n}'
                            n += 1
                        used_stems.add(str(dst_stem))
                        jobs.append((str(src), str(dst_stem)))
                        items['images'].append(
                            f'{slug}/{sec_slug}/{dst_stem.name}')
                    else:
                        items[key].append((fn, relp))
                    counts[key.rstrip('s')] = counts.get(key.rstrip('s'), 0) + 1
            if any(items.values()):
                secs[str(rel)] = {'name': sec_name, **items}
        if secs:
            lst = [secs[k] for k in
                   sorted(secs, key=lambda k: (k != '.', natural_key(k)))]
            merged = []
            for s in lst:
                if merged and merged[-1]['name'] == s['name']:
                    for key in ('images', 'videos', 'raw', 'docs'):
                        merged[-1][key] += s[key]
                else:
                    merged.append(s)
            sections[slug] = merged
        stats[slug] = counts
    return jobs, sections, stats


def write_module(sections, stats):
    extra, cards, num = [], [], 11
    for folder, slug, mode in FOLDERS:
        title = titleize(folder)
        secs = sections.get(slug, [])
        cover = secs[0]['images'][0] if secs and secs[0]['images'] else None
        if mode == 'new' and secs:
            sector, loc = META[slug]
            has_media = bool(secs)
            meta = f'{sector} — {loc}'
            n_photos = sum(len(s['images']) for s in secs)
            desc = (f'A {sector.lower()} project in {loc} — documented by OPRELL '
                    f'across {n_photos} photographs, shown below in the '
                    'original site sections.' if has_media else
                    f'A {sector.lower()} project in {loc} — documented by '
                    'OPRELL. Photography to follow.')
            extra.append(dict(
                slug=slug, num=f'{num:02d}', title=title, meta=meta,
                sector=sector, location=loc,
                status='Delivered' if has_media else 'Documentation pending',
                desc=desc, quote=None, images=[],
                cover=cover, sections=secs))
            num += 1
        if mode == 'new' and not secs:
            continue
        cards.append((slug, title,
                      META.get(slug, ('', ''))[1] or 'Dubai', cover))
    body = '# GENERATED by import_projects.py — do not edit; re-run the script\n\n'
    body += 'SECTIONS = ' + repr(sections) + '\n\n'
    body += 'EXTRA_PROJECTS = ' + repr(extra) + '\n\n'
    body += 'INDEX_CARDS = ' + repr(cards) + '\n'
    OUT_PY.write_text(body, encoding='utf-8')
    return extra, cards


def main():
    jobs, sections, stats = scan()
    todo = [j for j in jobs
            if not Path(j[1] + '.webp').exists()
            or not Path(j[1] + '-800.webp').exists()]
    print(f'{len(jobs)} images found, {len(todo)} to convert', flush=True)
    errs = []
    if todo:
        with ProcessPoolExecutor() as ex:
            for i, r in enumerate(ex.map(_job, todo, chunksize=8), 1):
                if r:
                    errs.append(r)
                if i % 50 == 0 or i == len(todo):
                    print(f'  {i}/{len(todo)}', flush=True)
    extra, cards = write_module(sections, stats)
    print(json.dumps(stats, indent=1))
    print(f'wrote {OUT_PY} — {len(extra)} new projects, '
          f'{sum(len(s["images"]) for v in sections.values() for s in v)} images')
    if errs:
        print('ERRORS:')
        for e in errs:
            print(' ', e)


if __name__ == '__main__':
    main()
