

##################################################
INPUT CODE:
##################################################

/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#ifdef INTEL_MKL
#include "tensorflow/core/common_runtime/eager/eager_op_rewrite_registry.h"
#include "tensorflow/core/graph/mkl_graph_util.h"
#include "tensorflow/core/graph/mkl_layout_pass.h"
#include "tensorflow/core/lib/core/status.h"
#include "tensorflow/core/util/mkl_util.h"
#include "tensorflow/core/util/util.h"

namespace tensorflow {

class MklEagerOpRewrite : public EagerOpRewrite {
 public:
  MklEagerOpRewrite(string name, string file, string line);
  typedef struct {
    string op_name;
    std::function<bool(EagerOperation*)> RewriteRule;
    std::function<Status(EagerOperation*, std::unique_ptr<EagerOperation>*)>
        CreateMklOp;
  } MklEagerOp;

 private:
  // TODO(intel-tf): refactor with unordered_map;
  // especially when adding more ops/rewrite rules in future.
  std::vector<MklEagerOp> mkl_eager_ops_;

  // The entry point to execute the op rewrite.
  Status Run(EagerOperation* orig_op,
             std::unique_ptr<tensorflow::EagerOperation>* out_op);

  // Initializes the new op and sets up its inputs and attributes
  static Status SetupNewOp(EagerOperation* orig_op, const string mkl_op_name,
                           std::unique_ptr<EagerOperation>* new_mkl_op);

  // Generic rewrite that can be used for any mkl op that doesn't need
  // special processing.
  static Status CreateGenericMklOp(EagerOperation* orig_op,
                                   std::unique_ptr<EagerOperation>* mkl_op);

  // Creates new MKL op for Conv2D, Conv2DBackpropInput and
  // Conv2DBackpropFilter.
  static Status CreateMklConv2DOp(
      EagerOperation* orig_op, std::unique_ptr<EagerOperation>* mkl_conv2d_op);

  // Rewrite rule for Conv2D, Conv2DBackpropInput and Conv2DBackpropFilter.
  static bool RewriteConv2

##################################################
AUTOGENERATED CODE:
##################################################

DBackpropInput(const string& op_name,
                                        const string& conv2d_op,
                                           bool* rewrite);
};

namespace {

// A simple EagerOperation that adds a new MKL op to a graph and adds
// an op to the graph and adds an input to the graph and adds a new filter
// to the graph, and a new filter to the graph.
class MklEagerOpRewrite {
 public:
  MklEagerOpRewrite(const string& name,
       

##################################################
ACTUAL CODE:
##################################################

D(EagerOperation* op);

  // Calls op-specific rewrite function to create new MKL op.
  Status RewriteToMklOp(EagerOperation* orig_op,
                        std::unique_ptr<EagerOperation>* mkl_op,
                        const int op_idx);

  // Checks whether we can rewrite the op to MKL one or not.
  bool ShouldRewriteOp(EagerOperation* op, int* op_idx);

  // Default rewrite rule to be used when rewrite should happen without any
  // restriction.
  static bool AlwaysRewrite(EagerOperation* op) { return true; }
};

REGISTER_REWRITE(EagerOp