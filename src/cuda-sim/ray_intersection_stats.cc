#include "ray_intersection_stats.h"
#include <iostream>
#include <cstdlib>
#include <cstring>

// 全局统计实例定义
RayIntersectionStats g_ray_stats;

// 环境变量控制开关
bool g_enable_ray_stats = false;

void init_ray_intersection_stats() {
    // 检查环境变量以启用统计收集
    const char* enable_stats = getenv("VULKAN_SIM_ENABLE_RAY_STATS");
    g_enable_ray_stats = (enable_stats != nullptr && 
                         (strcmp(enable_stats, "1") == 0 || 
                          strcmp(enable_stats, "true") == 0 || 
                          strcmp(enable_stats, "TRUE") == 0));
    
    if (g_enable_ray_stats) {
        printf("Ray intersection statistics collection ENABLED\n");
        printf("Use VULKAN_SIM_ENABLE_RAY_STATS=0 to disable\n");
        g_ray_stats.reset();
    } else {
        printf("Ray intersection statistics collection DISABLED\n");
        printf("Use VULKAN_SIM_ENABLE_RAY_STATS=1 to enable\n");
    }
}

void cleanup_ray_intersection_stats() {
    if (g_enable_ray_stats) {
        printf("\n=== Final Ray Intersection Statistics ===\n");
        g_ray_stats.print_stats();
        
        // 可选：保存到文件
        const char* output_file = getenv("VULKAN_SIM_RAY_STATS_FILE");
        if (output_file) {
            g_ray_stats.save_to_file(output_file);
        } else {
            // 默认文件名
            g_ray_stats.save_to_file("ray_intersection_stats.csv");
        }
    }
}
