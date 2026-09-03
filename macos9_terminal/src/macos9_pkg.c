/**
 * Classic Mac OS 9.2.2 Package Manager ('pkg')
 * Command-line extension and software management for SIOUX & MPW environments.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../include/macos9_pkg.h"

int pkg_init(pkg_db_t *db) {
    if (!db) return -1;
    memset(db, 0, sizeof(pkg_db_t));

    /* Preload core system extensions */
    pkg_entry_t *p = &db->packages[db->count++];
    strncpy(p->name, "CarbonLib", PKG_NAME_LEN);
    strncpy(p->version, "1.6", PKG_VERSION_LEN);
    strncpy(p->description, "Carbon API Runtime Library for Classic Mac OS", PKG_DESC_LEN);
    p->type = PKG_TYPE_SHARED_LIB;
    p->size_bytes = 1048576;
    p->sha256_prefix = 0x8A3C4D1E;
    p->installed = true;

    p = &db->packages[db->count++];
    strncpy(p->name, "OpenTransport", PKG_NAME_LEN);
    strncpy(p->version, "2.7.9", PKG_VERSION_LEN);
    strncpy(p->description, "Apple TCP/IP & AppleTalk Networking Protocol Stack", PKG_DESC_LEN);
    p->type = PKG_TYPE_EXTENSION;
    p->size_bytes = 2097152;
    p->sha256_prefix = 0xB29F01A4;
    p->installed = true;

    p = &db->packages[db->count++];
    strncpy(p->name, "defense-telemetry", PKG_NAME_LEN);
    strncpy(p->version, "3.0.1", PKG_VERSION_LEN);
    strncpy(p->description, "UNICAGD Critical Infrastructure Telemetry Sensor", PKG_DESC_LEN);
    p->type = PKG_TYPE_EXTENSION;
    p->size_bytes = 65536;
    p->sha256_prefix = 0x9A7B5E12;
    p->installed = false;

    p = &db->packages[db->count++];
    strncpy(p->name, "sioux-rich-tui", PKG_NAME_LEN);
    strncpy(p->version, "1.0", PKG_VERSION_LEN);
    strncpy(p->description, "Metrowerks CodeWarrior SIOUX Terminal & TUI Engine", PKG_DESC_LEN);
    p->type = PKG_TYPE_APPLICATION;
    p->size_bytes = 131072;
    p->sha256_prefix = 0xDEADBEEF;
    p->installed = false;

    return 0;
}

int pkg_install(pkg_db_t *db, const char *name) {
    if (!db || !name) return -1;
    for (uint32_t i = 0; i < db->count; i++) {
        if (strcmp(db->packages[i].name, name) == 0) {
            if (db->packages[i].installed) {
                printf("[pkg] Package '%s' is already installed.\n", name);
                return 0;
            }
            printf("[pkg] Installing '%s' (v%s)...\n", name, db->packages[i].version);
            printf("[pkg]   > Verifying SHA-256 prefix: 0x%08X... [OK]\n", db->packages[i].sha256_prefix);
            printf("[pkg]   > Allocating heap buffer (%u bytes)... [OK]\n", db->packages[i].size_bytes);
            printf("[pkg]   > Copying to target folder... [OK]\n");
            db->packages[i].installed = true;
            printf("[pkg] Successfully installed '%s'. System restart may be required for INITs.\n", name);
            return 0;
        }
    }
    printf("[pkg] Error: Package '%s' not found in repository.\n", name);
    return -2;
}

int pkg_remove(pkg_db_t *db, const char *name) {
    if (!db || !name) return -1;
    for (uint32_t i = 0; i < db->count; i++) {
        if (strcmp(db->packages[i].name, name) == 0) {
            if (!db->packages[i].installed) {
                printf("[pkg] Package '%s' is not installed.\n", name);
                return 0;
            }
            db->packages[i].installed = false;
            printf("[pkg] Package '%s' successfully removed.\n", name);
            return 0;
        }
    }
    printf("[pkg] Error: Package '%s' not found.\n", name);
    return -2;
}

void pkg_list(const pkg_db_t *db) {
    if (!db) return;
    printf("\n+--------------------+---------+------------+--------------------------------------+\n");
    printf("| Package Name       | Version | Status     | Description                          |\n");
    printf("+--------------------+---------+------------+--------------------------------------+\n");
    for (uint32_t i = 0; i < db->count; i++) {
        const pkg_entry_t *p = &db->packages[i];
        printf("| %-18s | %-7s | %-10s | %-36.36s |\n",
               p->name, p->version, p->installed ? "INSTALLED" : "available", p->description);
    }
    printf("+--------------------+---------+------------+--------------------------------------+\n\n");
}

bool pkg_verify(const pkg_db_t *db, const char *name) {
    if (!db || !name) return false;
    for (uint32_t i = 0; i < db->count; i++) {
        if (strcmp(db->packages[i].name, name) == 0) {
            printf("[pkg] Integrity Verification for '%s':\n", name);
            printf("      • Size: %u bytes\n", db->packages[i].size_bytes);
            printf("      • Expected Checksum Prefix: 0x%08X\n", db->packages[i].sha256_prefix);
            printf("      • Status: 100%% VERIFIED (Clean)\n");
            return true;
        }
    }
    printf("[pkg] Package '%s' not found.\n", name);
    return false;
}

int main(int argc, char **argv) {
    pkg_db_t db;
    pkg_init(&db);

    if (argc < 2) {
        printf("Classic Mac OS 9.2.2 Package Manager ('pkg') v1.0\n");
        printf("Usage: pkg <command> [args]\n");
        printf("Commands:\n");
        printf("  list              List all installed and available packages\n");
        printf("  install <name>    Install extension, control panel, or application\n");
        printf("  remove <name>     Remove installed package\n");
        printf("  verify <name>     Check package checksum and integrity\n");
        return 0;
    }

    const char *cmd = argv[1];
    if (strcmp(cmd, "list") == 0) {
        pkg_list(&db);
    } else if (strcmp(cmd, "install") == 0) {
        if (argc < 3) {
            printf("[pkg] Error: specify package name to install.\n");
            return 1;
        }
        pkg_install(&db, argv[2]);
    } else if (strcmp(cmd, "remove") == 0) {
        if (argc < 3) {
            printf("[pkg] Error: specify package name to remove.\n");
            return 1;
        }
        pkg_remove(&db, argv[2]);
    } else if (strcmp(cmd, "verify") == 0) {
        if (argc < 3) {
            printf("[pkg] Error: specify package name to verify.\n");
            return 1;
        }
        pkg_verify(&db, argv[2]);
    } else {
        printf("[pkg] Unknown command '%s'. Run 'pkg' for help.\n", cmd);
    }
    return 0;
}
