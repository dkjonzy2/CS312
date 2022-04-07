#!/usr/bin/python3

from PyQt6.QtCore import QLineF, QPointF


# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1


class GeneSequencing:

    def __init__(self):
        self.banded = None

    # This is the method called by the GUI.  _seq1_ and _seq2_ are two sequences to be aligned, _banded_ is a boolean that tells
    # you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
    # how many base pairs to use in computing the alignment

    def align(self, seq1, seq2, banded, align_length):
        self.banded = banded
        self.MaxCharactersToAlign = align_length

        seq1 = "-" + seq1 # Add a blank symbol to the beginning of each string so that beginning is always a match
        seq2 = "-" + seq2

        AlignmentA = ""
        AlignmentB = ""

        ## Unrestricted
        if not banded:
            width = min(align_length + 1, len(seq1))
            height = min(align_length + 1, len(seq2))
            table = [[float('inf') for i in range(height)] for j in range(width)] # Initialize tables
            prevTable = [[0 for i in range(height)] for j in range(width)]


            table[0][0] = 0 # Set start point values
            prevTable[0][0] = 'stop'
            for i in range(1, width): # Set base cases
                table[i][0] = table[i - 1][0] + INDEL
                prevTable[i][0] = 'l'
            for j in range(1, height):
                table[0][j] = table[0][j - 1] + INDEL
                prevTable[0][j] = 'u'

            for i in range(1, width): # Fill in entire table from top left
                for j in range(1, height):
                    left = table[i - 1][j] + INDEL
                    top = table[i][j - 1] + INDEL
                    if seq1[i] == seq2[j]:  # If the letters match then set value to MATCH, else SUB
                        diag = table[i - 1][j - 1] + MATCH
                    else:
                        diag = table[i - 1][j - 1] + SUB
                    minimum = min(left, top, diag)
                    table[i][j] = minimum
                    if minimum == left:  # Determine which input was used and store in previous pointer
                        prevTable[i][j] = 'l'
                    elif minimum == top:
                        prevTable[i][j] = 'u'
                    elif minimum == diag:
                        prevTable[i][j] = 'm'

            score = table[-1][-1]

            # Get Alignment not Banded
            A = seq1
            B = seq2
            i = min(len(A) - 1, align_length) # Set the start point
            j = min(len(B) - 1, align_length) # Set the start point
            while i > 0 or j > 0: # While i and j are both above 0 meaning we have not reached the beginning
                if j > 0 and prevTable[i][j] == 'u': # If previous was u then continue trace in upper
                    AlignmentA = "−" + AlignmentA
                    AlignmentB = B[j] + AlignmentB
                    j -= 1
                elif i > 0 and prevTable[i][j] == 'l': # If previous was l then continue in left
                    AlignmentA = A[i] + AlignmentA
                    AlignmentB = "−" + AlignmentB
                    i -= 1
                elif i > 0 and j > 0 and prevTable[i][j] == 'm': # If previous was m then continue on diagonal
                    AlignmentA = A[i] + AlignmentA
                    AlignmentB = B[j] + AlignmentB
                    i -= 1
                    j -= 1
                else:
                    print("Backtrace Failed") # If none matched then the trace was lost (should never happen)
                    exit(-111)

        # Restricted
        if banded:
            width = min(align_length + 1, len(seq1))
            height = min(align_length + 1, len(seq2))

            if abs(width - height) > 100:  # Significant difference in length, return not calculable
                print("No alignment possible as sequence differ in length significantly")
                score = float('inf')
                alignment1 = "No Alignment Possible"
                alignment2 = "No Alignment Possible"
                return {'align_cost': score, 'seqi_first100': alignment1, 'seqj_first100': alignment2}

            width = 1 + MAXINDELS * 2 # Initialize tables
            table = [[float('inf') for i in range(7)] for j in range(height)]
            prevTable = [[0 for i in range(7)] for j in range(height)]

            table[0][0] = 0 # Set start values
            prevTable[0][0] = 'stop'
            for i in range(1, 4): # Set base cases
                table[0][i] = table[0][i - 1] + INDEL
                prevTable[0][i] = 'u'
            for i in range(1, height): # Fill table from top left
                for j in range(width):
                    if i > MAXINDELS: # Use these comparisons once values are being shifted in table
                        if j + 1 > width - 1:  # Get north value
                            north = float('inf')
                        else:
                            north = table[i - 1][j + 1] + INDEL
                        if j - 1 < 0:  # Get west value
                            west = float('inf')
                        else:
                            west = table[i][j - 1] + INDEL
                        adjust = min(MAXINDELS - i, 0)
                        if j - adjust < len(seq1) and seq1[j - adjust] == seq2[i]:  # Check for match
                            nw = table[i - 1][j] + MATCH
                        else:
                            nw = table[i - 1][j] + SUB
                        minimum = min(north, west, nw)
                        table[i][j] = minimum

                        if minimum == north: # Determine which value was previous
                            prevTable[i][j] = 'u'
                        elif minimum == west:
                            prevTable[i][j] = 'l'
                        else:
                            prevTable[i][j] = 'm'

                    else:  # For the first 3 rows that don't need adjustment, run like unbanded
                        north = table[i - 1][j] + INDEL
                        west = table[i][j - 1] + INDEL
                        if seq1[i] == seq2[j]:
                            diag = table[i - 1][j - 1] + MATCH
                        else:
                            diag = table[i - 1][j - 1] + SUB
                        minimum = min(north, west, diag)
                        table[i][j] = minimum
                        if minimum == north:
                            prevTable[i][j] = 'u'
                        elif minimum == west:
                            prevTable[i][j] = 'l'
                        else:
                            prevTable[i][j] = 'm'

            # Get Alignment Banded
            A = seq2
            B = seq1
            i = min(len(A) - 1, align_length)
            j = min(len(B) - 1, align_length)
            while i > 0 or j > 0:
                if i > MAXINDELS: # For when table is shifted, use these comparisons
                    adjust = j - i + MAXINDELS
                    if i > 0 and j > 0 and prevTable[i][adjust] == 'l': # Check left
                        AlignmentA = "−" + AlignmentA
                        AlignmentB = B[j] + AlignmentB
                        j -= 1
                    elif i > 0 and prevTable[i][adjust] == 'u':  # Check top
                        AlignmentA = A[i] + AlignmentA
                        AlignmentB = "−" + AlignmentB
                        i -= 1
                    elif j > 0 and prevTable[i][adjust] == 'm':  # Check diag
                        AlignmentA = A[i] + AlignmentA
                        AlignmentB = B[j] + AlignmentB
                        i -= 1
                        j -= 1
                    else:
                        print("Backtrace Failed")
                        exit(-111)
                else: # When table is not shifted (first 3 rows)
                    if i > 0 and prevTable[i][j] == 'l':
                        AlignmentA = A[i] + AlignmentA
                        AlignmentB = "−" + AlignmentB
                        i -= 1
                    elif j > 0 and prevTable[i][j] == 'u':
                        AlignmentA = "−" + AlignmentA
                        AlignmentB = B[j] + AlignmentB
                        j -= 1
                    elif i > 0 and j > 0 and prevTable[i][j] == 'm':
                        AlignmentA = A[i] + AlignmentA
                        AlignmentB = B[j] + AlignmentB
                        i -= 1
                        j -= 1
                    else:
                        print("Backtrace Failed")
                        exit(-111)


            # This is easier than changing the above code to switch the strings
            sub = AlignmentA
            AlignmentA = AlignmentB
            AlignmentB = sub

            i = min(len(A) - 1, align_length) # Get the length of str1
            j = min(len(B) - 1, align_length) # Get length of str2
            score = table[i][-abs(j-i)+MAXINDELS] # Get location of final score (Will depend on offset between i and j)

        alignment1 = AlignmentA[:100]
        alignment2 = AlignmentB[:100]
        ###################################################################################################

        return {'align_cost': score, 'seqi_first100': alignment1, 'seqj_first100': alignment2}
