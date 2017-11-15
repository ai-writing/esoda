java -cp "stanford-corenlp-full-2016-10-31/*" -Xmx12g edu.stanford.nlp.pipeline.StanfordCoreNLP -props "esl_paper.properties" -filelist tolist.txt -outputDirectory parsed 2> result.txt
