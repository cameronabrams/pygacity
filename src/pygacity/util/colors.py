def blend(hex1, hex2, t=0.5):
    """Blend two hex colors. t=0 returns hex1, t=1 returns hex2."""
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f'#{r:02x}{g:02x}{b:02x}'

# Primary
DrexelBlue   = '#07294d'
DrexelGold   = '#ffc600'

# Complementary — dark
DrexelTeal       = '#006699'
DrexelCrimson    = '#971b2f'
DrexelOlive      = '#949300'
DrexelOrange     = '#de7c00'

# Complementary — light
DrexelSkyBlue    = '#6cace4'
DrexelTomato     = '#d14124'
DrexelLime       = '#b7bf10'
DrexelAmber      = '#ff8f1c'

# Neutral
DrexelCharcoal   = '#333333'
DrexelSageGray   = '#bac5b9'
DrexelWarmGray   = '#bfb8af'
DrexelLightGray  = '#d0d3d4'

# Aliases
DrexelYellow = DrexelGold    # legacy name
DrexelLink   = DrexelTeal    # legacy name

# NC State University
# Core palette
NCSUWolfpackRed      = '#cc0000'
NCSUWolfpackBlack    = '#000000'
NCSUWolfpackWhite    = '#ffffff'

# Expanded palette
NCSUReynoldsRed      = '#990000'
NCSUPyromanFlame     = '#d14905'
NCSUHuntYellow       = '#fac800'
NCSUGenomicGreen     = '#6f7d1c'
NCSUCarmichaelAqua   = '#008473'
NCSUInnovationBlue   = '#427e93'
NCSUBioIndigo        = '#4156a1'

# University of Hawaii system — one primary color per campus
UHSystem             = '#b3995d'

# Universities
UHManoa              = '#024731'
UHHilo               = '#d52b1e'
UHWestOahu           = '#a71930'

# Community Colleges
HawaiiCC             = '#91004b'
HonoluluCC           = '#008c95'
KapiolaniCC          = '#002395'
KauaiCC              = '#8246af'
LeewardCC            = '#418fde'
UHMauiCollege        = '#005172'
WindwardCC           = '#7ab800'
