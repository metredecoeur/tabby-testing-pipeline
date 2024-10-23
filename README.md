# Emacs text editor package for integration with Tabby coding assistant

## Engineering thesis

Marta Borek\
318635\
Thesis supervisor: dr. hab. inż. Robert Nowak, prof uczelni

## Diploma thesis contents

Initial version of the work, based on the LaTeX template provided by the
faculty lies in the **thesis** directory. For the time being it consists
of the title and the academic entities and the persons involved.

## Setting up Tabby server

Scripts with docker commands from the installation tutorial on [official
Tabby
page](https://tabby.tabbyml.com/docs/quick-start/installation/docker/)
are to be found in the **tabby~localserversetup~** folder. For all of
the steps it is best to check with the official guide, as the
installation methods vary and it covers them all in detail, as well as
the dependencies necessary for the CUDA option.

## Open source AI coding assistants comparison

Side by side comparison of a selection of other open source projects is
to be found in **docs/open~sourceAIassistantscomparison~.pdf** file.

## Current research state and TODOs

### Programme architecture and design

1.  Client-server

    1.  1-Tier Structure

        -   User interface, business logic and data logic are all on one
            system.
        -   Client and server are on the same system.
        -   [ ] Check if applicable also to the situation where server
            is being locally hosted (docker etc), but most likely this
            is the right scenario.

    2.  2-Tier Structure

        -   Two separate machines acting as server and client
        -   Usually a desktop and a more powerful server
        -   Typically user system interface located on the client and db
            management and services are on the more powerful server

        1.  Fat Client-Thin Server

            Both application logic and user interface at client\'s end.

        2.  Thin Client-Fat Server

            Both application logic and db management at server\'s end.

2.  Potential development to existing tabby-mode

    1.  Automatic completion

        -   Current version only supports manual completion upon
            executing tabby-complete function
        -   For example:
            -   async process that gathers the necessary data for the
                request body after **n** miliseconds of idle time
            -   presents the first choice from the response
                -   preferably like in most IDE\'s using a grayed out
                    text
                -   might also be a box of some sort, like with
                    IntelliSense
            -   user can then
                -   cycle between different choices returned (if more
                    than one) with a specified keybinding
                -   accept the current choice with another keybinding

    2.  Chat Completion

        -   New chat functionality to add

3.  Tabby-agent

    -   Node.js package communicating with Tabby server
    -   Developed as part of the VSCode extension
    -   Implements:
        -   Debouncing (timing of requests sending)
        -   Caching (No need for additional duplicate server requests)
        -   Post-processing (picks a selection of best suggestions)

    [tabby-agent Language Server
    Protocol](https://tabby.tabbyml.com/blog/2024/02/05/create-tabby-extension-with-language-server-protocol/)
    [github tabby-agent
    documentation](https://github.com/TabbyML/tabby/tree/main/clients/tabby-agent)

    1.  [TODO]{.todo .TODO} Analysis of VSCode and Vim plugins

# Quality measuring and testing

## Simple text similarity comparison

### Algorithms

1.  Edit-based

    -   Also known as Distance-Based
    -   Measure the minimum number of single-character operations
        (insertions, deletions, substitutions) required to transform one
        string into another.
    -   The more, the greater the **distance** -\> worse similarity
    -   Examples:
        -   Hamming
        -   Levenshtein
        -   Damerau-Levenshtein
        -   Smith-Waterman

2.  Token-based

    -   Comparison based on tokens instead of single characters
    -   Examples:
        -   Jaccard
        -   Sorensen-Dice
        -   Tversky - generalization of the above two

3.  Sequence-based

    -   Focused more on analyzing and comparing the entire sequence as
        opposed to token based algorithms where we compare tokens in the
        sequence
    -   Examples:
        -   Ratcliff-Obershelp
        -   Longest common substring/subsequence

## Code Functionality similarity comparison

Based on [A systematic literature review on source code similarity measurement and clone detection by M. Zakeri-Nasrabadi et al.](https://www.researchgate.net/publication/371943883_A_systematic_literature_review_on_source_code_similarity_measurement_and_clone_detection_techniques_applications_and_challenges) there is an
overlap in clone code detection methods with the Simple text similarity
approach.

### Clones classification

1.  Type I

    Code snippets are exactly the same with the only differences in
    white spaces

2.  Type II

    -   Structure remains the same
    -   Names of variables etc may vary

3.  Type III

    -   Names vary
    -   Structural changes
    -   Some parts may be added/deleted/updated

4.  Type IV

    -   Compared snippets are totally different in terms of plain text
    -   Their functionality is virtually the same

### Detection techniques

1.  Text-based

    -   Usually no preprocessing (apart from whitespaces/comments
        removal)
    -   Mostly for Ist and IInd types of clones
    -   Methods:
        -   Burrows et al. (local alignment procedure, approximate
            string matching algorithm)
        -   *NICAD* (most-used, text normalization)
        -   Cosma and Joy, tool *PlaGate*, LSA matrix)

2.  Token-based

    -   Text converted to tokens sequences
    -   Sequences compared to find common subsequences
    -   Increased preprocessing time
    -   Does not fare well with type IV clones
    -   Methods:
        -   Rehman *LSC Miner* tool (multiple langs, focus on Java, C,
            C++)
        -   Lopes *SourcererCC* (C++ js, java, python)
        -   *CPDP*
        -   *SCSDS* (avoids the impact of structural modifications)
        -   *CP-Miner* tool, *CloSpan* subsequence mining algorithm

3.  Tree-based

    -   Source code converted to AST/parse tree
    -   Followed by the search for similar subtrees
    -   Time consuming for larger codebases
    -   Requires specifric parser for every language
    -   Matching subtrees is computationally expensive
    -   Accurate recognition of types I-III
    -   Methods:
        -   *DECKARD*
        -   *Tekchandani* (for type IV)
        -   *TECCD* tool with *word2vec* algorithm (ANTLR parser
            generator)
        -   *FAXIM* model (mostly Java)

4.  Graph-based

    -   Program Dependance Graph created for code snippets
        -   Each node are program statements
        -   Edges are data or control dependencies
    -   Followed by comparison between the graphs
    -   Can identify all types of clones
    -   NP-complete problem
    -   Constructing PDG for large codebases is time-consuming and prone
        to errors.
    -   Methods

5.  Learning-based

    -   Require large datasets of clean code, which may not be available
        for all languages
    -   Approaches based on Random Forest among the most promising ones
    -   

6.  Hybrid methods

    -   Combine 2 or more from the previous methods

7.  Test-based methods

    -   The **Black-box**-y approach
    -   The only one with the dynamic analysis approach
    -   Sample test inputs
    -   Runtime data collected
    -   Suitable for detecting type IV
    -   Methods:
        -   *EvoSuite* test data generation tool
            -   Computationally expensive to generate test cases for
                different methods


# Extending the (algorithm) codebase to use during quality testing

-   [github link to algorithms
    codebase](https://github.com/thealgorithms)

# Comparison with other tools

-   References from *AI-driven Software Development Source Code Quality*
    by BC. Petr Kantek
