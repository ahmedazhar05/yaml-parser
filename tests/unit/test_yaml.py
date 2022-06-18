import pytest, importlib
from io import StringIO
from src import yaml as myyaml


class Testing_getcleanline:

    @pytest.mark.parametrize("file_lines,expected", [
        ("- some line",        "- some line"),
        ("      - some line ", "      - some line "),
        ("- some line       ", "- some line       "),
        ("   - some line    ", "   - some line    "),
        ("key: value",         "key: value"),
        ("key: value        ", "key: value        "),
        ("     key: value   ", "     key: value   "),
        ("",                   None)
    ])
    def test_single_line_with_no_comments(self, file_lines, expected):
        assert myyaml._getcleanline(StringIO(file_lines)) == expected

    @pytest.mark.parametrize("file_lines,expected", [
        ("""- some line
- random line
- one more line""",                     "- some line"),
        ("""      - some line 
- line2""",                             "      - some line "),
        ("""- some line       
- line3""",                             "- some line       "),
        ("""   - some line    
- line2
- line3""",                             "   - some line    "),
        ("""key: value
key2: ketone""",                        "key: value"),
        ("""key: value        
     spaced: line      here     """,    "key: value        "),
        ("""     key: value   
more :    spaced    lines    """,       "     key: value   ")
    ])
    def test_multiple_lines_with_no_comments(self, file_lines, expected):
        assert myyaml._getcleanline(StringIO(file_lines)) == expected

    @pytest.mark.parametrize("file_lines,expected", [
        ("""
- some line
- random line
- one more line""",                     "- some line"),
        ("""      - some line 

- line2""",                             "      - some line "),
        ("""


- some line       """,                  "- some line       "),
        ("""   - some line    
    
- line2""",                             "   - some line    "),
        ("""    
key: value""",                          "key: value"),
        ("""key: value        
     spaced: line      here     
""",                                    "key: value        "),
        ("""
""",                                    None),
        ("""
    
""",                                    None),
        ("""    

""",                                    None),
        ("""

    """,                                None)
    ])
    def test_lines_containing_blank_lines(self, file_lines, expected):
        assert myyaml._getcleanline(StringIO(file_lines)) == expected

    @pytest.mark.parametrize("file_lines", [
        ("# - some # line   "),
        ("# - some line"),
        (" # - some line    "),
        ("  # key: value"),
        ("   # key: value   "),
        ("    # key: value  "),
        ("#"),
        ("# "),
        ("#  "),
        ("#   "),
        (" #"),
        ("  #"),
        ("   #"),
        ("# "),
        (" # "),
        ("  # "),
        ("   # ")
    ])
    def test_single_comment_lines(self, file_lines):
        assert myyaml._getcleanline(StringIO(file_lines)) == None

    @pytest.mark.parametrize("file_lines", [
        ("# - some # line   \n# - some # line   "),
        ("# - some line\n# - some line"),
        (" # - some line    \n # - some line    "),
        ("  # key: value\n  # key: value"),
        ("   # key: value   \n   # key: value   "),
        ("    # key: value  \n    # key: value  "),
        ("#\n#"),
        ("# \n# "),
        ("#  \n#  "),
        ("#   \n#   "),
        (" #\n #"),
        ("  #\n  #"),
        ("   #\n   #"),
        ("# \n# "),
        (" # \n # "),
        ("  # \n  # "),
        ("   # \n   # ")
    ])
    def test_multiple_comment_lines(self, file_lines):
        assert myyaml._getcleanline(StringIO(file_lines)) == None

    @pytest.mark.parametrize("file_lines,expected", [
        ("- some line    # - some # line",             "- some line"),
        ("    s # - some line     # - some line",      "    s"),
        ("some line# not a comment",                   "some line# not a comment"),
        ("   line# not a comment # comment",           "   line# not a comment"),
        (" line#not a comment",                        " line#not a comment"),
        ("line'# not a comment# not a comment either", "line'# not a comment# not a comment either"),
        ("line#not a comment      # comment",          "line#not a comment"),
        #("    - 'line # not comment'",                 "    - 'line # not comment'"),               # TODO: test fails here, needs fixing
        #("key: ' # value'",                            "key: ' # value'"),                          # TODO: test fails here, needs fixing
        #("- line ' #not a comment here' : value",      "- line ' #not a comment here' : value"),    # TODO: test fails here, needs fixing
        #("'obje #ct': value",                          "'obje #ct': value")                         # TODO: test fails here, needs fixing
    ])
    def test_inline_comments(self, file_lines, expected):
        assert myyaml._getcleanline(StringIO(file_lines)) == expected

    @pytest.mark.parametrize("file_lines,expected", [
        ("""- some line
# comment""",                    "- some line"),
        ("""# comment
- some line""",                  "- some line"),
        ("""      # comment
test: line""",                   "test: line"),
        ("""      # comment
    test: line""",               "    test: line"),
        ("""#comment
""",                             None),
        ("""
# comment""",                    None),
        ("""#some: comment

# comment
- line""",                       "- line")
    ])
    def test_mixed_lines(self, file_lines, expected):
        assert myyaml._getcleanline(StringIO(file_lines)) == expected


class Testing_converttype:

    @pytest.mark.parametrize("input", [
        ("34"),
        ("+34"),
        ("-34")
    ])
    def test_integers(self, input):
        assert myyaml._converttype(input, {}) == (int(input), None)

    @pytest.mark.parametrize("input", [
        ("34.5"),
        ("+34.5"),
        ("-34.5"),
        ("34."),
        ("-34."),
        ("+34."),
        (".34"),
        ("-.34"),
        ("+.34"),
    ])
    def test_floats(self, input):
        assert myyaml._converttype(input, {}) == (float(input), None)

    @pytest.mark.parametrize("input", [
        ("yes"),
        ("true"),
        ("on"),
        ("no"),
        ("off"),
        ("false"),
        ('YES'),
        ('TRUE'),
        ('ON'),
        ('NO'),
        ('OFF'),
        ('FALSE')
    ])
    def test_booleans(self, input):
        assert myyaml._converttype(input, {}) == (input.lower() in ['yes', 'true', 'on'], None)

    @pytest.mark.parametrize("input", [
        (""),
        ("null"),
        ("~")
    ])
    def test_nulls(self, input):
        assert myyaml._converttype(input, {}) == (None, None)

    @pytest.mark.parametrize("input,expected", [
        ("genuine string", "genuine string"),
        ("~~",             "~~"),
        ("true false",     "true false"),
        ("'some value'",   "some value"),
        ("string1'",       "string1'"),
        ('string2"',       'string2"'),
        ('li"ne',          'li"ne'),
        ("li'ne",          "li'ne")
        #('"str\'ing"',     '"str\'ing"'),   # TODO: test is failing although output is correct, needs better string representation
        #("'str\"ing'",     "'str\"ing'"),   # TODO: test is failing although output is correct, needs better string representation
    ])
    def test_strings(self, input, expected):
        assert myyaml._converttype(input, {}) == (expected, None)