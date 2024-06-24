# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

from marshmallow import ValidationError
from app.backend.service.classes.data_augmentation.augmentation_methods.eda.eda_algorithm_code.code.eda import *

# * Removed - The file function is called directly by the surrounding program, no need for parsig arguments. *
# arguments to be parsed from command line
# import argparse
# ap = argparse.ArgumentParser()
# ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
# ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
# ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
# ap.add_argument("--alpha_sr", required=False, type=float, help="percent of words in each sentence to be replaced by synonyms")
# ap.add_argument("--alpha_ri", required=False, type=float, help="percent of words in each sentence to be inserted")
# ap.add_argument("--alpha_rs", required=False, type=float, help="percent of words in each sentence to be swapped")
# ap.add_argument("--alpha_rd", required=False, type=float, help="percent of words in each sentence to be deleted")
# args = ap.parse_args()

# #the output file
# output = None
# if args.output:
#     output = args.output
# else:
#     from os.path import dirname, basename, join
#     output = join(dirname(args.input), 'eda_' + basename(args.input))

# * Removed | Moved - Default values are not necessary since they can be set directly inside the funtion header. Moved validation into gen_eda() function. Adapted checks to adhere to new function construction. *
# number of augmented sentences to generate per original sentence
# num_aug = 9 #default
# if args.num_aug:
#     num_aug = args.num_aug

# #how much to replace each word by synonyms
# alpha_sr = 0.1#default
# if args.alpha_sr is not None:
#     alpha_sr = args.alpha_sr

# #how much to insert new words that are synonyms
# alpha_ri = 0.1#default
# if args.alpha_ri is not None:
#     alpha_ri = args.alpha_ri

# #how much to swap words
# alpha_rs = 0.1#default
# if args.alpha_rs is not None:
#     alpha_rs = args.alpha_rs

# #how much to delete words
# alpha_rd = 0.1#default
# if args.alpha_rd is not None:
#     alpha_rd = args.alpha_rd

# if alpha_sr == alpha_ri == alpha_rs == alpha_rd == 0:
#      ap.error('At least one alpha should be greater than zero')


# generate more data with standard augmentation
# * Removed "train_orig, output_file," since we call the gen_eda function directly. Changed 'num_aug=9' to 1. Added "sentence" to pass a sentence for augmentation. *
def gen_eda(sentence, alpha_sr, alpha_ri, alpha_rs, alpha_rd, num_aug=1):
    # * Removed - No need to read in or create a file *
    # writer = open(output_file, 'w')
    # lines = open(train_orig, 'r').readlines()

    # * Removed - No need to extract sentences and split them *
    # for i, line in enumerate(lines):
    #     parts = line[:-1].split('\t')
    #     label = parts[0]
    #     sentence = parts[1]

    # * Added - As previously described. *
    if alpha_sr == alpha_ri == alpha_rs == alpha_rd == 0:
        raise ValidationError('At least one alpha must be greater than zero.')

    aug_sentences = eda(sentence, alpha_sr=alpha_sr, alpha_ri=alpha_ri,
                        alpha_rs=alpha_rs, p_rd=alpha_rd, num_aug=num_aug)

    # * Added - Directly return the augmented sentence. *
    return aug_sentences[0]
    # * Removed - No need to write results to a new file *
    # for aug_sentence in aug_sentences:
    #     writer.write(label + "\t" + aug_sentence + '\n')

    # * Removed - No need to close the file writer or print the results *
    # writer.close()
    # print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

# * Removed - No need for a main file check and function call. *
# main function
# if __name__ == "__main__":

#     #generate augmented sentences and output into a new file
#     gen_eda(args.input, output, alpha_sr=alpha_sr, alpha_ri=alpha_ri, alpha_rs=alpha_rs, alpha_rd=alpha_rd, num_aug=num_aug)
