// Abel Kahsai
// June 19, 2025

// Static Cont-Kukanov allocator

function allocate(order_size, venues, lambda_over, lambda_under, theta_queue) {
    const step = 100;
    let splits = [[]]; // start with an empty allocation list
  
    for (let v = 0; v < venues.length; v++) {
      const new_splits = [];
      for (const alloc of splits) {
        const used = alloc.reduce((a, b) => a + b, 0);
        const max_v = Math.min(order_size - used, venues[v].ask_size);
  
        for (let q = 0; q <= max_v; q += step) {
          new_splits.push([...alloc, q]);
        }
      }
      splits = new_splits;
    }
  
    let best_cost = Infinity;
    let best_split = [];
  
    for (const alloc of splits) {
      const total = alloc.reduce((a, b) => a + b, 0);
      if (total !== order_size) continue;
  
      const cost = compute_cost(alloc, venues, order_size, lambda_over, lambda_under, theta_queue);
      if (cost < best_cost) {
        best_cost = cost;
        best_split = alloc;
      }
    }
  
    return { best_split, best_cost };
  }
  
  function compute_cost(split, venues, order_size, lambda_over, lambda_under, theta) {
    let executed = 0;
    let cash_spent = 0;
  
    for (let i = 0; i < venues.length; i++) {
      const exe = Math.min(split[i], venues[i].ask_size);
      executed += exe;
      cash_spent += exe * (venues[i].ask + venues[i].fee);
      const maker_rebate = Math.max(split[i] - exe, 0) * venues[i].rebate;
      cash_spent -= maker_rebate;
    }
  
    const underfill = Math.max(order_size - executed, 0);
    const overfill = Math.max(executed - order_size, 0);
    const risk_penalty = theta * (underfill + overfill);
    const cost_penalty = lambda_under * underfill + lambda_over * overfill;
  
    return cash_spent + risk_penalty + cost_penalty;
  }
  