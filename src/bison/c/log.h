
#ifndef DEBUG
    #define DEBUG 1
#endif


#if __STDC_VERSION__ >= 199901L
    #ifndef DEBUG_PRINT
        #ifdef DEBUG
            #define DEBUG_PRINT \
                (printf("%s(%d)-<%s>: ", __FILE__, __LINE__, __FUNCTION__),printf)
        #else
            #ifndef __OPTIMIZE__
                #define DEBUG_PRINT \
                    (printf("%s(%d)-<%s>: ", __FILE__, __LINE__, __FUNCTION__),printf)
            #else
                #define DEBUG_PRINT(...) ;
            #endif
        #endif
    #endif
#else
    #ifndef DEBUG_PRINT
        #ifdef DEBUG
            #define DEBUG_PRINT \
                (printf("%s(%d)-<%s>: ", __FILE__, __LINE__, __FUNCTION__),printf)
        #else
            #ifndef __OPTIMIZE__
                #define DEBUG_PRINT \
                    (printf("%s(%d)-<%s>: ", __FILE__, __LINE__, __FUNCTION__),printf)
            #else
                #define DEBUG_PRINT(...) ;
            #endif
        #endif
    #endif
#endif



