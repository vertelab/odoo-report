# Central selection lists shared across Elevata modules.
# Import these instead of redefining in each module:
#   from odoo.addons.elevata_base.constants import RATE_TYPE, CONTRACT_TYPE, ...

CONTRACT_TYPE = [
    ('SERV-VB', 'On Demand'),
    ('SERV-STD', 'Standard'),
    ('SERV-FULL', 'Full Service'),
    ('SERV-GAR', 'Warranty'),
]

VISITS_PER_YEAR = [
    ('1', '1 visit/year'),
    ('2', '2 visits/year'),
    ('4', '4 visits/year'),
    ('6', '6 visits/year'),
]

LINE_TYPE = [
    ('arbete', 'Labor'),
    ('material', 'Material'),
    ('resa', 'Travel'),
    ('nodtelefon', 'Emergency Phone'),
    ('besiktning', 'Supplementary Inspection'),
    ('ovrigt', 'Other'),
]

RATE_TYPE = [
    ('normaltid', 'Normal hours (Mon-Fri 07:00-16:00)'),
    ('overtid_1_2h', 'Overtime 1-2 h'),
    ('overtid_2h_plus', 'Overtime after 2 h'),
    ('lordag', 'Saturday'),
    ('sondag_helgdag', 'Sunday / Public holiday'),
    ('storhelg', 'Major holiday'),
    ('beredskap_vardag', 'On-call weekday'),
    ('beredskap_helg', 'On-call weekend'),
    ('jourutryckning', 'Emergency call-out (min 3 h)'),
    ('restid', 'Travel time'),
    ('servicebil_mil', 'Service vehicle (per 10 km)'),
    ('servicebil_tid', 'Service vehicle time'),
    ('servicebil_fast', 'Service vehicle fixed fee'),
    ('verktygsavgift', 'Tool fee'),
]
