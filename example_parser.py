 Return to ChrTable.py CVS log   Up to [CVS] / biopy-pgml / Bio / PGML / Arabidopsis / AtDB 

--------------------------------------------------------------------------------
File: [CVS] / biopy-pgml / Bio / PGML / Arabidopsis / AtDB / ChrTable.py (download)
Revision 1.1.1.1 (vendor branch), Wed Dec 20 21:02:02 2000 UTC (7 years, 11 months ago) by chapmanb 
Branch: pgml, MAIN 
CVS Tags: biopy-pgml_20001220, HEAD_NEW, HEAD
Changes since 1.1: +0 -0 lines
Initial PGML import

 

--------------------------------------------------------------------------------

"""Parse Arabidopsis Chromosome information from on-line tables.
"""

# standard modules
import htmllib
import formatter
import string

class ChrTableParser(htmllib.HTMLParser):
    """A parser for the Arabidopsis sequenced BAC clone tables.

    This parses out the useful information from the tables at:
    http://www.arabidopsis.org/cgi-bin/maps/Seqtable.pl
    and sticks it into TableRowRecord() classes.

    The information parsed is available after the parse via the
    all_rows attribute of the parser.
    """
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)

        self.all_rows = []
        self.current_row = None
        self.in_row = 0

        # info for each row
        self.in_contig = 0

        self.in_col_two = 0
        self.in_seq_clone = 0

        self.in_col_three = 0
        self.in_acc_num = 0

        self.in_orientation = 0

        self.in_size = 0

        self.in_col_six = 0
        self.in_markers = 0
        self.current_marker = ''

        self.in_col_seven = 0
        self.in_repeats = 0

        self.in_col_eight = 0
        self.in_five_prime = 0

        self.in_col_nine = 0
        self.in_three_prime = 0

    def _restart_row(self):
        if self.current_row:
            #print self.current_row
            self.all_rows.append(self.current_row)
        
        self.in_row = 1
        self.td_counter = 0
        self.current_row = TableRowRecord()
        
    def start_tr(self, attrs):
        """Signal when we get to the beginning of a new row.

        New rows start with:
        '<tr align=left>'
        """
        if len(attrs) == 1:
            if attrs[0][0] == 'align' and attrs[0][1] == 'left':
                self._restart_row()

    def start_td(self, attrs):
        """Keep track of the number of td elements encountered.

        This increments a counter and sets some boolean variables to help
        us keep track of what column  we are in, in a row.
        """
        if self.in_row:
            self.td_counter = self.td_counter + 1

            if self.td_counter == 1:
                self.in_contig = 1
            elif self.td_counter == 2:
                self.in_col_two = 1
            elif self.td_counter == 3:
                self.in_col_three = 1
            elif self.td_counter == 4:
                self.in_orientation = 1
            elif self.td_counter == 5:
                self.in_size = 1
            elif self.td_counter == 6:
                self.in_col_six = 1
            elif self.td_counter == 7:
                self.in_col_seven = 1
            elif self.td_counter == 8:
                self.in_col_eight = 1
            elif self.td_counter == 9:
                self.in_col_nine = 1

    def end_td(self):
        """Unset flags which are not unset by other code.

        Some table items can contain multiple items, so the flag cannot be
        unset directly in other code. This helps make these unsets.
        """
        if self.in_col_two:
            self.in_col_two = 0
        elif self.in_col_three:
            self.in_col_three = 0
        elif self.in_col_six:
            self.in_col_six = 0
        elif self.in_col_seven:
            self.in_col_seven = 0
        elif self.in_col_eight:
            self.in_col_eight = 0
        elif self.in_col_nine:
            self.in_col_nine = 0

    def start_a(self, attrs):
        """Keep track of anchor tags inside of td elements."""
        if self.in_col_two:
            self.in_seq_clone = 1
            self.in_col_two = 0
        elif self.in_col_three:
            self.in_acc_num = 1
            self.in_col_three = 0
        elif self.in_col_six:
            self.in_markers = 1
        elif self.in_col_seven:
            self.in_repeats = 1
        elif self.in_col_eight:
            self.in_five_prime = 1
            self.in_col_eight = 0
        elif self.in_col_nine:
            self.in_three_prime = 1
            self.in_col_nine = 0

    def handle_data(self, text):
        """Actually extract the data we want.

        Based on the flag set, this will put the text information into
        the current_row record class as the appropriate attribute.
        """
        if self.in_contig:
            if string.strip(text):
                self.current_row.contig = string.strip(text)
            self.in_contig = 0
        elif self.in_seq_clone:
            if string.strip(text):
                self.current_row.sequenced_clone = string.strip(text)
            self.in_seq_clone = 0
        elif self.in_acc_num:
            if string.strip(text):
                self.current_row.accession_num = string.strip(text)
            self.in_acc_num = 0
        elif self.in_orientation:
            if string.strip(text):
                self.current_row.orientation = string.strip(text)
            self.in_orientation = 0
        elif self.in_size:
            if string.strip(text):
                self.current_row.size = string.strip(text)
            self.in_size = 0
        elif self.in_markers:
            if string.strip(text):
                self.current_row.markers[string.strip(text)] = -1
                self.current_marker = string.strip(text)
            self.in_markers = 0
        # if we are in col six, but not in a marker, then we have
        # position info for the marker
        elif self.in_col_six and not(self.in_markers):
            if not(self.current_marker == ''):
                pos_info = int(text[1:-1])
                self.current_row.markers[self.current_marker] = pos_info
                self.current_marker = ''

        elif self.in_repeats:
            if string.strip(text):
                self.current_row.simple_repeats.append([string.strip(text), -1])
                self.current_repeat = string.strip(text)
            self.in_repeats = 0
        elif self.in_col_seven and not(self.in_repeats):
            pos_info = int(text[1:-1])
            self.current_row.simple_repeats[-1][1] = pos_info

        elif self.in_five_prime:
            if string.strip(text):
                self.current_row.five_prime_neighbor = string.strip(text)
            self.in_five_prime = 0
        elif self.in_three_prime:
            if string.strip(text):
                self.current_row.three_prime_neighbor = string.strip(text)
            self.in_three_prime = 0

    def end_html(self):
        """At the end of a parse we need to add the last row info."""
        if self.current_row:
            # print self.current_row
            self.all_rows.append(self.current_row)
            
            
class TableRowRecord:
    """Represent a row in the Arabidopsis clone table.

    This is just meant as a simple way to hold the information in a single
    row of the clone table. Each item of information is held as an attribute
    of this class.

    Numerical information that is not present in the table defaults to a
    value of -1. String information that is not present defaults to the
    string '<blank>'.
    """
    def __init__(self):
        self.contig = -1
        self.sequenced_clone = '<blank>'
        self.accession_num = '<blank>'
        self.orientation = '<blank>'
        self.size = -1
        self.markers = {}
        # a 2D list, where list[0] is the repeat type and list[1] is position
        self.simple_repeats = []
        self.five_prime_neighbor = '<blank>'
        self.three_prime_neighbor = '<blank>'

        self.useful_id = '<not assigned>'

    def __str__(self):
        """Provides a quick and dirty way to verify the information.

        A 'print <TableRowRecordObject>' will print out all of the pertinent
        info so you can verify it is correct.
        """
        return ("(%s=>%s; %s=>%s; %s=>%s; %s=>%s; %s=>%s;" %
                ('contig', self.contig, 'sequenced_clone', self.sequenced_clone,
                 'accession_num', self.accession_num, 'orientation',
                 self.orientation, 'size', self.size) +
                "%s=>%s; %s=>%s; %s=>%s; %s=>%s)" %
                ('markers', self.markers, 'simple_repeats', self.simple_repeats,
                 'five_prime_neighbor', self.five_prime_neighbor,
                 'three_prime_neighbor', self.three_prime_neighbor))
    
        
def parse_table(file_handle):
    """Parses out a handle containing an htmlized Arabidopsis table.

    Returns the information as a list of TableRowRecord objects.
    """
    abs_formatter = formatter.NullFormatter()
    parser = ChrTableParser(abs_formatter)

    parser.feed(file_handle.read())

    return parser.all_rows

