/*
 * Copyright (C) 2023 Huawei Technologies Co.,Ltd. All rights reserved.
 * SPDX-License-Identifier: MIT
 */

#ifndef CONFIG_H
#define CONFIG_H

#define NB_THREADS 8

#define RUN_DURATION_SECONDS 3

#include <vsync/spinlock/ticketlock.h>
typedef ticketlock_t lock_t;
#define lock_init ticketlock_init
#define lock_acquire ticketlock_acquire
#define lock_release ticketlock_release

#endif /* CONFIG_H */
