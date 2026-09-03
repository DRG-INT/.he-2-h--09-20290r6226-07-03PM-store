#ifndef MACOS9_PKG_H
#define MACOS9_PKG_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PKG_MAX_PACKAGES    64
#define PKG_NAME_LEN        32
#define PKG_VERSION_LEN     16
#define PKG_DESC_LEN        64

typedef enum {
    PKG_TYPE_EXTENSION,     /* System Folder:Extensions: (INIT/dext) */
    PKG_TYPE_CONTROL_PANEL, /* System Folder:Control Panels: */
    PKG_TYPE_SHARED_LIB,    /* System Folder:Extensions: (CFM shlib) */
    PKG_TYPE_APPLICATION    /* Macintosh HD:Applications: */
} pkg_type_t;

typedef struct {
    char        name[PKG_NAME_LEN];
    char        version[PKG_VERSION_LEN];
    char        description[PKG_DESC_LEN];
    pkg_type_t  type;
    uint32_t    size_bytes;
    uint32_t    sha256_prefix; /* Checksum prefix */
    bool        installed;
} pkg_entry_t;

typedef struct {
    uint32_t    count;
    pkg_entry_t packages[PKG_MAX_PACKAGES];
} pkg_db_t;

/* Package Manager API */
int  pkg_init(pkg_db_t *db);
int  pkg_install(pkg_db_t *db, const char *name);
int  pkg_remove(pkg_db_t *db, const char *name);
void pkg_list(const pkg_db_t *db);
bool pkg_verify(const pkg_db_t *db, const char *name);

#ifdef __cplusplus
}
#endif

#endif /* MACOS9_PKG_H */
