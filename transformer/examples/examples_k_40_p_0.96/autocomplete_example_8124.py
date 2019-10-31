

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
#include "tensorflow/core/common_runtime/eager/process_function_library_runtime.h"

#include <iterator>
#include <memory>
#include <utility>

#include "tensorflow/core/lib/core/errors.h"
#include "tensorflow/core/lib/gtl/array_slice.h"
#include "tensorflow/core/util/reffed_status_callback.h"

namespace tensorflow {
namespace eager {

#if!defined(IS_MOBILE_PLATFORM)
Status EagerFunctionArgs::GetLocalArg(const int index, Tensor* val) const {
  const absl::optional<Tensor>& arg = tensor_args_->at(index);
  if (arg.has_value()) {
    *val = arg.value();
    return Status::OK();
  } else {
    return errors::NotFound("Argument ", index, " has no local tensor.");
  }
}

Status EagerFunctionArgs::GetRemoteArg(const int index,
                                       RemoteTensorHandle* val) const {
  return serialize_remote_handle_(index, val);
}

void EagerProcessFunctionLibraryRuntime::RunRemoteDevice(
    const FunctionLibraryRuntime::Options& opts,
    FunctionLibraryRuntime::Handle local_handle, const InternalArgsView& args,
    std::vector<Tensor>* rets,
    FunctionLibraryRuntime::DoneCallback done) const {
  if (!rets->empty()) {
    done(
        errors::Unimplemented("Remote outputs are not supported by "
                              "EagerClusterFunctionLibraryRuntime yet."));
    return;
  }
  if (!args.local_args.empty()) {
    done(
        errors::Unimplemented("Local inputs are not by supported by "
                              "EagerClusterFunctionLibraryRuntime."));
    return;
  }
  if (args.remote_args == nullptr) {
    done(
        errors::Internal("EagerClusterFunctionLibraryRuntime: remote_args "
                         "should never be null."));
    return;
 

##################################################
AUTOGENERATED CODE:
##################################################


  }

  local_handle_ = rets->front()[...done]->device.handle;
  strings::StrAppend(&local_handle_, nullptr, args);

  // TODO(ebrevdo,gj: Figure out how we resolve non-tensor arrays
  // (including strings).
  if (args->count("empty") || args->count("out_tensor") ||
        args->count("error_message") || args->count("message") || args->count("resolve_err") ||
       args->count("resolve_error"):
    return;

  // We handle a range of values with the given number of elements and should always
  // handle values with the same number of elements. Otherwise it may be difficult to
  // handle tensors with incompatible values without increasing the complexity of
  // the

##################################################
ACTUAL CODE:
##################################################

 }
  parent_->Run(opts, local_handle, args.remote_args, std::move(done));
}

void EagerProcessFunctionLibraryRuntime::Run(
    const FunctionLibraryRuntime::Options& opts,
    FunctionLibraryRuntime::Handle handle, const FunctionArgsInterface& args,
    std::vector<Tensor>* rets,
    FunctionLibraryRuntime::DoneCallback done) const {
  auto* cleanup_items = new std::vector<std::unique_ptr<CleanUpItem>>;
  done = ApplyCleanUpToDoneCallback(cleanup_items, done);

  auto get_component_args = [&args](const ComponentFunctionData& comp_data,
                                    InternalArgs*