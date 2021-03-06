

##################################################
INPUT CODE:
##################################################

/* Copyright 2018 The TensorFlow Authors. All Rights Reserved.

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
#ifndef TENSORFLOW_CORE_COMMON_RUNTIME_EAGER_EAGER_OPERATION_H_
#define TENSORFLOW_CORE_COMMON_RUNTIME_EAGER_EAGER_OPERATION_H_

#include "tensorflow/core/common_runtime/eager/attr_builder.h"
#include "tensorflow/core/common_runtime/eager/context.h"
#include "tensorflow/core/common_runtime/eager/eager_executor.h"
#include "tensorflow/core/common_runtime/eager/tensor_handle.h"
#include "tensorflow/core/framework/cancellation.h"
#include "tensorflow/core/util/device_name_utils.h"

namespace tensorflow {
class EagerOperation {
 public:
  EagerOperation(tensorflow::EagerContext* ctx, const char* op,
                 bool is_function, const tensorflow::AttrTypeMap* t,
                 EagerExecutor* executor = nullptr)
      : ctx_(nullptr) {
    Reset(ctx, op, is_function, t, executor);
  }

  ~EagerOperation() {
    for (tensorflow::TensorHandle* h : inputs_) {
      h->Unref();
    }
  }

  // An EagerOperation object can be reused for a different op by calling
  // Clear(), and then Reset(...) with the same arguments that would have
  // been provided to the constructor.
  void Clear() {
    ctx_ = nullptr;  // Sign that state is now cleared
    for (tensorflow::TensorHandle* h : inputs_) {
      h->Unref();
    }
    inputs_.clear();
  }

  void Reset(tensorflow::EagerContext* ctx, const char* op, bool is_function,
             const tensorflow::AttrTypeMap* t, EagerExecutor* executor) {
    DCHECK(ctx_ == nullptr) << "Calling Reset without first calling Release";
    DCHECK(inputs_.empty());
    ctx_ = ctx;
    if (attrs_ == nullptr) {
      attrs_.reset(new tensorflow::AttrBuilder(op));
    } else {
      attrs_->Reset(op);
    }
 

##################################################
AUTOGENERATED CODE:
##################################################


    return;
  }

  EagerOperation(const char* name, const char* attr_value) {
    return attr_value;
  }

  void Clear() {
    for (const auto& attr_value : attr_value) {
      attr_value.reset();
    }
  }

  // The following is a copy of the EagerOperation's constructor. The
  // constructor itself is not owned, but is owned by EagerContext.
  EagerOperation* Create() {
    return Create();
  }

  // EagerOperation's constructor is a reference to this object, but not a
  // EagerContext.
  void SetEagerOperation(const EagerOperation* o) {
    EagerContext* context = o;
    context->set_oper

##################################################
ACTUAL CODE:
##################################################

   attr_types_ = t;
    device_ = nullptr;
    device_name_ = DeviceNameUtils::ParsedName();
    use_xla_ = false;
    is_function_ = is_function;
    cancellation_manager_ = nullptr;
    executor_ = executor? executor : (ctx? &ctx->Executor() : nullptr);
#ifdef TENSORFLOW_MEM_DEBUG
    op_name_ = op;
#endif
  }

  bool is_function() const { return is_function_; }

  tensorflow::EagerContext* EagerContext() { return ctx_; }

  tensorflow::AttrBuilder* MutableAttrs() { return attrs_.get(); }
  const tensorflow::AttrBuilder