#ifndef RAY_INTERSECTION_STATS_H
#define RAY_INTERSECTION_STATS_H

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

// 线程安全的光线相交统计计数器
struct RayIntersectionStats {
    // Ray-Box相交统计
    std::atomic<uint64_t> ray_box_tests_total;          // 总的Ray-Box测试次数
    std::atomic<uint64_t> ray_box_hits;                 // Ray-Box命中次数
    std::atomic<uint64_t> ray_box_misses;               // Ray-Box未命中次数
    
    // Ray-Triangle相交统计
    std::atomic<uint64_t> ray_triangle_tests_total;     // 总的Ray-Triangle测试次数
    std::atomic<uint64_t> ray_triangle_hits;            // Ray-Triangle命中次数
    std::atomic<uint64_t> ray_triangle_misses;          // Ray-Triangle未命中次数
    
    // BVH遍历统计
    std::atomic<uint64_t> bvh_nodes_visited;            // 访问的BVH节点数
    std::atomic<uint64_t> leaf_nodes_visited;           // 访问的叶子节点数
    std::atomic<uint64_t> inner_nodes_visited;          // 访问的内部节点数
    
    // 光线追踪统计
    std::atomic<uint64_t> rays_traced_total;            // 总追踪光线数
    std::atomic<uint64_t> rays_with_hits;               // 有命中的光线数
    std::atomic<uint64_t> rays_without_hits;            // 无命中的光线数

    // 构造函数 - 初始化所有计数器为0
    RayIntersectionStats() {
        reset();
    }

    // 重置所有计数器
    void reset() {
        ray_box_tests_total.store(0);
        ray_box_hits.store(0);
        ray_box_misses.store(0);
        
        ray_triangle_tests_total.store(0);
        ray_triangle_hits.store(0);
        ray_triangle_misses.store(0);
        
        bvh_nodes_visited.store(0);
        leaf_nodes_visited.store(0);
        inner_nodes_visited.store(0);
        
        rays_traced_total.store(0);
        rays_with_hits.store(0);
        rays_without_hits.store(0);
    }

    // 原子地增加Ray-Box测试计数
    void increment_ray_box_test() {
        ray_box_tests_total.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加Ray-Box命中计数
    void increment_ray_box_hit() {
        ray_box_hits.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加Ray-Box未命中计数
    void increment_ray_box_miss() {
        ray_box_misses.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加Ray-Triangle测试计数
    void increment_ray_triangle_test() {
        ray_triangle_tests_total.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加Ray-Triangle命中计数
    void increment_ray_triangle_hit() {
        ray_triangle_hits.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加Ray-Triangle未命中计数
    void increment_ray_triangle_miss() {
        ray_triangle_misses.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加BVH节点访问计数
    void increment_bvh_node_visited() {
        bvh_nodes_visited.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加叶子节点访问计数
    void increment_leaf_node_visited() {
        leaf_nodes_visited.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加内部节点访问计数
    void increment_inner_node_visited() {
        inner_nodes_visited.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加追踪光线计数
    void increment_ray_traced() {
        rays_traced_total.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加有命中光线计数
    void increment_ray_with_hit() {
        rays_with_hits.fetch_add(1, std::memory_order_relaxed);
    }

    // 原子地增加无命中光线计数
    void increment_ray_without_hit() {
        rays_without_hits.fetch_add(1, std::memory_order_relaxed);
    }

    // 打印统计信息
    void print_stats(const char* prefix = "") const {
        printf("=== %sRay Intersection Statistics ===\n", prefix);
        
        // Ray-Box统计
        uint64_t box_total = ray_box_tests_total.load();
        uint64_t box_hits = ray_box_hits.load();
        uint64_t box_misses = ray_box_misses.load();
        printf("Ray-Box Tests:\n");
        printf("  Total:  %lu\n", box_total);
        printf("  Hits:   %lu (%.2f%%)\n", box_hits, 
               box_total > 0 ? (100.0 * box_hits / box_total) : 0.0);
        printf("  Misses: %lu (%.2f%%)\n", box_misses,
               box_total > 0 ? (100.0 * box_misses / box_total) : 0.0);
        
        // Ray-Triangle统计
        uint64_t tri_total = ray_triangle_tests_total.load();
        uint64_t tri_hits = ray_triangle_hits.load();
        uint64_t tri_misses = ray_triangle_misses.load();
        printf("Ray-Triangle Tests:\n");
        printf("  Total:  %lu\n", tri_total);
        printf("  Hits:   %lu (%.2f%%)\n", tri_hits,
               tri_total > 0 ? (100.0 * tri_hits / tri_total) : 0.0);
        printf("  Misses: %lu (%.2f%%)\n", tri_misses,
               tri_total > 0 ? (100.0 * tri_misses / tri_total) : 0.0);
        
        // BVH遍历统计
        uint64_t nodes_visited = bvh_nodes_visited.load();
        uint64_t leaf_visited = leaf_nodes_visited.load();
        uint64_t inner_visited = inner_nodes_visited.load();
        printf("BVH Traversal:\n");
        printf("  Nodes Visited: %lu\n", nodes_visited);
        printf("  Leaf Nodes:    %lu (%.2f%%)\n", leaf_visited,
               nodes_visited > 0 ? (100.0 * leaf_visited / nodes_visited) : 0.0);
        printf("  Inner Nodes:   %lu (%.2f%%)\n", inner_visited,
               nodes_visited > 0 ? (100.0 * inner_visited / nodes_visited) : 0.0);
        
        // 光线追踪统计
        uint64_t rays_total = rays_traced_total.load();
        uint64_t rays_hit = rays_with_hits.load();
        uint64_t rays_miss = rays_without_hits.load();
        printf("Ray Tracing:\n");
        printf("  Rays Traced:   %lu\n", rays_total);
        printf("  Rays Hit:      %lu (%.2f%%)\n", rays_hit,
               rays_total > 0 ? (100.0 * rays_hit / rays_total) : 0.0);
        printf("  Rays Miss:     %lu (%.2f%%)\n", rays_miss,
               rays_total > 0 ? (100.0 * rays_miss / rays_total) : 0.0);
        
        // 效率统计
        printf("Efficiency Metrics:\n");
        if (rays_total > 0) {
            printf("  Avg Box Tests/Ray:      %.2f\n", (double)box_total / rays_total);
            printf("  Avg Triangle Tests/Ray: %.2f\n", (double)tri_total / rays_total);
            printf("  Avg Nodes Visited/Ray:  %.2f\n", (double)nodes_visited / rays_total);
        }
        
        printf("========================================\n");
    }

    // 保存统计信息到文件
    void save_to_file(const char* filename) const {
        FILE* f = fopen(filename, "w");
        if (!f) {
            printf("Error: Cannot open file %s for writing\n", filename);
            return;
        }
        
        fprintf(f, "# Ray Intersection Statistics\n");
        fprintf(f, "ray_box_tests_total,%lu\n", ray_box_tests_total.load());
        fprintf(f, "ray_box_hits,%lu\n", ray_box_hits.load());
        fprintf(f, "ray_box_misses,%lu\n", ray_box_misses.load());
        fprintf(f, "ray_triangle_tests_total,%lu\n", ray_triangle_tests_total.load());
        fprintf(f, "ray_triangle_hits,%lu\n", ray_triangle_hits.load());
        fprintf(f, "ray_triangle_misses,%lu\n", ray_triangle_misses.load());
        fprintf(f, "bvh_nodes_visited,%lu\n", bvh_nodes_visited.load());
        fprintf(f, "leaf_nodes_visited,%lu\n", leaf_nodes_visited.load());
        fprintf(f, "inner_nodes_visited,%lu\n", inner_nodes_visited.load());
        fprintf(f, "rays_traced_total,%lu\n", rays_traced_total.load());
        fprintf(f, "rays_with_hits,%lu\n", rays_with_hits.load());
        fprintf(f, "rays_without_hits,%lu\n", rays_without_hits.load());
        
        fclose(f);
        printf("Statistics saved to %s\n", filename);
    }
};

// 全局统计实例
extern RayIntersectionStats g_ray_stats;

// 环境变量控制开关
extern bool g_enable_ray_stats;

// 初始化统计系统
void init_ray_intersection_stats();

// 清理统计系统
void cleanup_ray_intersection_stats();

// 便利宏定义，用于条件统计（避免不必要的原子操作开销）
#define RAY_STATS_INCREMENT_BOX_TEST() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_box_test(); } while(0)

#define RAY_STATS_INCREMENT_BOX_HIT() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_box_hit(); } while(0)

#define RAY_STATS_INCREMENT_BOX_MISS() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_box_miss(); } while(0)

#define RAY_STATS_INCREMENT_TRIANGLE_TEST() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_triangle_test(); } while(0)

#define RAY_STATS_INCREMENT_TRIANGLE_HIT() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_triangle_hit(); } while(0)

#define RAY_STATS_INCREMENT_TRIANGLE_MISS() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_triangle_miss(); } while(0)

#define RAY_STATS_INCREMENT_BVH_NODE_VISITED() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_bvh_node_visited(); } while(0)

#define RAY_STATS_INCREMENT_LEAF_NODE_VISITED() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_leaf_node_visited(); } while(0)

#define RAY_STATS_INCREMENT_INNER_NODE_VISITED() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_inner_node_visited(); } while(0)

#define RAY_STATS_INCREMENT_RAY_TRACED() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_traced(); } while(0)

#define RAY_STATS_INCREMENT_RAY_HIT() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_with_hit(); } while(0)

#define RAY_STATS_INCREMENT_RAY_MISS() \
    do { if (g_enable_ray_stats) g_ray_stats.increment_ray_without_hit(); } while(0)

#endif // RAY_INTERSECTION_STATS_H
