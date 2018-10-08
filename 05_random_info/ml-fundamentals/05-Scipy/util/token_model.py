'''
Module setting up a TokenModel for tokenizing tweets.
'''
import numpy as np
import re
from scipy.sparse import coo_matrix, find
from collections import Counter


# Regex to split tweets on whitespace and symbols, leaving .@#$^ prefixes
TOK_SPLIT_RE = re.compile(r'\W*\s+[^\w\.\@\#\$\^]*')


# Regex to trim symbols from the end
TRIM_END_SYMBOLS_RE = re.compile(r'\W+\Z')

class TokenModel:
    '''
    Simplified/Hard-coded model following fit/transform pattern.

    Where fit establishes tokens and their frequencies so that transform
    can vectorize, replacing low-frequency and/or unknown tokens with the
    "_UNK" token.
    '''
    def __init__(self, min_freq=5):
        '''
        Initialize the model.

        :param min_freq: Frequency cutoff such that tokens with
                         freq<=min_freq are treated as unknown.
        '''
        self._tok2freq = Counter()
        self._min_freq = min_freq
        self._collapse_res = [
            ('_USER', re.compile(r'^\.?\@.*$')),
            ('_HASHTAG', re.compile(r'^#.*$')),
            ('_TICKER', re.compile(r'^\$.*$')),
            ('_SIGNED', re.compile(r'^\^.*$')),
            ('_URL', re.compile(r'^[a-zA-Z]+://.+$')),
            ('_EMAIL', re.compile(r'^\w+\@.+$')),
        ]
        self._tok2idx = None
        self._idx2tok = None

    @property
    def tok2freq(self):
        ''' Get the token to frequency_count counter. '''
        return self._tok2freq

    def get_freq_cutoff(self):
        freqs = np.array([value for _,value in self.tok2freq.most_common()], dtype=np.int32)
        return np.where(freqs <= 5)[0][0]

    def tok2idx(self, token):
        '''
        Get the index of the token or -1.

        :param token: Normalized token or collapsed token marker
        :return: The frequency-ordered index for the token or -1

        NOTE: -1 will be returned if this model has not been fit
              or does not have the _UNK token.
        '''
        result = -1
        if self._tok2idx is None:
            if len(self._tok2freq) > 0:
                self._tok2idx = {
                    token: idx
                    for idx, (token, _) in enumerate(self._tok2freq.most_common())
                }
        if self._tok2idx is not None:
            result = self._tok2idx.get(token, self._tok2idx.get('_UNK', -1))
        return result

    def idx2tok(self, idx):
        '''
        Get the token at the given index or '_UNK'.

        :param idx: The frequency ordered index for the token.
        :return: The token at the index or '_UNK'.

        NOTE: '_UNK' will be returned if this model has not been fit
              or if the given index does not exist or if the index
              maps to the '_UNK' token.
        '''
        result = '_UNK'
        if self._idx2tok is None:
            if len(self._tok2freq) > 0:
                self._idx2tok = {
                    idx: token
                    for idx, (token, _) in enumerate(self._tok2freq.most_common())
                }
        if self._idx2tok is not None:
            result = self._idx2tok.get(idx, '_UNK')
        return result

    @staticmethod
    def split(tweet):
        '''
        Split a tweet into raw tokens

        :param tweet: A tweet string
        :return: A list of raw tokens.

        Where raw tokens are the exact tokens split from the tweet without
        normalizing or substituting special collapse token markers.
        '''
        return TOK_SPLIT_RE.split(tweet)

    def collapse(self, raw_tokens, no_unk=False, no_collapse=False):
        '''
        Collapse raw_tokens to final tokens.

        :param raw_tokens: Raw tokens as returned from "split".
        :param no_unk: When true, ignore frequency information.
        :param no_collapse: When true, don't collapse to token markers.
        :return: A list of final tokens.

        NOTE: If the model has not been fit, collapse behaves as if no_unk is True.

        Where final tokens are normalized and/or collapsed token markers, including:

        - _USER -- for all ".@user" and "@user" tokens
        - _HASHTAG -- for all "#hashtag" tokens
        - _TICKER -- for all "^ticker" tokens
        - _SIGNED -- for all "^signed" tokens
        - _URL -- for all url tokens
        - _EMAIL -- for all email tokens
        - _UNK -- for all "unknown" or low-frequency tokens (unless no_unk)

        And normalization lowercases all non-collapsed tokens.
        '''
        if len(self._tok2freq) == 0:
            # Turn off _UNK if model has not been fit.
            no_unk = True

        final_tokens = list()
        for token in raw_tokens:
            if not token:
                continue
            token = TRIM_END_SYMBOLS_RE.sub('', token)
            if not token:
                continue
            collapsed = False
            if not no_collapse:
                token, collapsed = self._do_collapse(token)
            if not collapsed:
                token = token.lower()
            if token:
                if not no_unk:
                    freq = self._tok2freq.get(token, self._min_freq)
                    if freq <= self._min_freq:
                        token = '_UNK'
                final_tokens.append(token)
        return final_tokens

    def _do_collapse(self, token):
        '''
        Collapse the token if possible.
        :param token: The token to collapse
        :return: (token, collapsed) where token is the original token if
                 collapsed is False; otherwise token is the collapse token.
        '''
        collapsed = False
        for collapse_token, collapse_re in self._collapse_res:
            if collapse_re.match(token):
                token = collapse_token
                collapsed = True
                break
        return token, collapsed

    def fit(self, tweets):
        '''
        Fit this model using the given sequence of tweets.
        '''
        self._tok2freq = Counter()
        self._tok2idx = None
        self._idx2tok = None
        for tweet in tweets:
            raw_tokens = self.split(tweet)
            for final_token in self.collapse(raw_tokens, no_unk=True):
                self._tok2freq[final_token] += 1
        self._tok2freq['_UNK'] = self._tok2freq.most_common(1)[0][1] + 1

    def partial_fit(self, tweet):
        '''
        Fit the given tweet for incremental fitting.
        Useful when the dataset is large and cannot be fully preloaded for fit.
        '''
        raw_tokens = self.split(tweet)
        for final_token in self.collapse(raw_tokens, no_unk=True):
            self._tok2freq[final_token] += 1

    def end_partial_fit(self):
        self._tok2freq['_UNK'] = self._tok2freq.most_common(1)[0][1] + 1

    def transform(self, tweet_or_tweets):
        '''
        Vectorize a tweet or sequence of tweets as a CSR matrix.

        :param tweet_or_tweets A tweet (str) or sequence of tweets to vectorize.
        :return: A sparse matrix with the vectorization of the single tweet or sequence of tweets.
        '''
        row = list()
        col = list()
        if isinstance(tweet_or_tweets, str):
            self._encode_tokens(tweet_or_tweets, 0, row, col)
        else:
            for idx, tweet in enumerate(tweet_or_tweets):
                self._encode_tokens(tweet, idx, row, col)
        data = np.ones(len(row), dtype=np.int8)
        return coo_matrix((data, (row, col))).tocsr()

    def partial_transform(self, dok_matrix, row_idx, tweet):
        for token in self._do_tokenize(tweet):
            dok_matrix[row_idx, self.tok2idx(token)] = 1

    def _encode_tokens(self, tweet, idx, row, col):
        '''
        Add encoded tweet #idx tokens for sparse storage into row and col.
        '''
        for token in self._do_tokenize(tweet):
            row.append(idx)
            col.append(self.tok2idx(token))

    def tokenize(self, tweet_or_tweets):
        '''
        Tokenize a tweet or sequence of tweets.

        :param tweet_or_tweets: A tweet (str) or sequence of tweets to tokenize.
        :return: A list of tokens for a tweet or a list of token lists for each tweet.
        '''
        if isinstance(tweet_or_tweets, str):
            return self._do_tokenize(tweet_or_tweets)
        else:
            result = list()
            for tweet in tweet_or_tweets:
                result.append(self._do_tokenize(tweet))
            return result

    def _do_tokenize(self, tweet):
        return self.collapse(self.split(tweet))

    @staticmethod
    def find_nonzero(sparse_matrix):
        '''
        Find the nonzero values in the sparse matrix.

        :param sparse_matrix: The sparse matrix whose non-zero values to find.
        :return: nzr, nzc, nzv, vcounts

        Where
        - nzr is an array containing the nonzero row indices
        - nzc is an array containing the nonzero col indices
        - nzv is an array containing the corresponding nonzero values
        - vcounts is an array containing the counts of integer values
        '''
        nzr, nzc, nzv = find(sparse_matrix)
        vcounts = np.bincount(nzv)
        return nzr, nzc, nzv, vcounts

    @staticmethod
    def show_vcounts(vcounts):
        for idx, count in enumerate(vcounts):
            if count > 0:
                print(f'{idx}: {count}')
