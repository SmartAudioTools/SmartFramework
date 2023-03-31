from SmartFramework.files import addToName, readLines, writeLines
from SmartFramework.files import dragAndDrop
from googletrans import Translator


def callback(paths):
    translator = Translator()
    for path in paths:
        print(path)
        lines = readLines(path)
        splitedCommentlines = []
        for line in lines:
            # print(repr(line))
            commentIndex = line.rfind("//")
            if commentIndex == -1:  # laisse sous forme de string
                splitedCommentlines.append(line)
            else:  # met sous forme de liste à traduire (sauf 1er element)
                trueCommentIndex = commentIndex + 2
                if trueCommentIndex < len(line) and line[trueCommentIndex] == "/":
                    # triple ///
                    trueCommentIndex += 1
                if trueCommentIndex < len(line) and line[trueCommentIndex] == " ":
                    trueCommentIndex += 1
                if trueCommentIndex < len(line):
                    if isinstance(splitedCommentlines[-1], list) and (
                        splitedCommentlines[-1][-1][-1] != "."
                    ):
                        splitedCommentlines[-1].append(
                            line[trueCommentIndex:]
                        )  # concatene commentaire avec celui de la ligne au dessus si commence par une minuscule pour permetre traduction en une phrase
                    else:
                        if (
                            trueCommentIndex < len(line)
                            and line[trueCommentIndex] == "@"
                        ):
                            # print(line)
                            # print(trueCommentIndex)
                            trueCommentIndex = line.find(" ", trueCommentIndex)
                            trueCommentIndex = line.find(" ", trueCommentIndex) + 1
                        splitedCommentlines.append(
                            [line[:trueCommentIndex], line[trueCommentIndex:]]
                        )
                else:
                    splitedCommentlines.append(line)
        comments = []
        for splitedCommentline in splitedCommentlines:
            if isinstance(splitedCommentline, list):
                comment = " ".join(splitedCommentline[1:])
                comments.append(comment)

        translatedCommentsIter = translator.translate(comments, dest="fr", src="en")
        translatedComments = []
        for translatedComment in translatedCommentsIter:
            translatedComments.append(translatedComment.text)
        newLines = []
        i = 0
        for splitedCommentline in splitedCommentlines:
            if isinstance(splitedCommentline, list):
                # translatedComment
                newLine = splitedCommentline[0] + translatedComments[i]
                i += 1
            else:
                newLine = splitedCommentline
            newLines.append(newLine)
        writeLines(addToName(path, "_fr"), newLines)


dragAndDrop(callback=callback, group=True, extension=["h", "cpp"])
