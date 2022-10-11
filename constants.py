from typing import Final

DATA_FOLDER: Final = './data/'
OUT_FOLDER: Final = './out/'

EPIAS_FOLDER: Final = DATA_FOLDER + 'epias/'
SLIDING_HOLIDAYS_JSON = DATA_FOLDER + 'sliding_holidays.json'

WANDB_PROJECT_NAME: Final = 'electricity-demand-forecasting'
WANDB_USER_NAME: Final = 'bertan-gunyel'
WANDB_DYNAMIC_VIS: Final = 'dynamic-vis'
WANDB_STATIC_VIS: Final = 'static-vis'
WANDB_ARTIFACT_STATIC_VIS: Final = WANDB_STATIC_VIS + '_artifact'
WANDB_HOURLY_ELECTRICITY_DEMAND_TABLE: Final = 'hourly-electricity-demand-table'
WANDB_HOURLY_AVERAGES_TABLE: Final = 'hourly-averages-table'


CONSUMPTION: Final = 'Consumption (MWh)'
HOLIDAY: Final = 'holiday'
WEEK_DAY: Final = 'week_day'
WEEKEND: Final = 'weekend'
YEAR: Final = 'year'
MONTH: Final = 'month'
DAY: Final = 'day'
QUARTER: Final = 'quarter'
HOUR: Final = 'hour'
ROLLING_MONTHLY_AVERAGE: Final = 'Rolling Monthly Average'

MONDAY: Final = 'Monday'
TUESDAY: Final = 'Tuesday'
WEDNESDAY: Final = 'Wednesday'
THURSDAY: Final = 'Thursday'
FRIDAY: Final = 'Friday'
SATURDAY: Final = 'Saturday'
SUNDAY: Final = 'Sunday'

RAMAZAN: Final = 'ramazan'
RAMAZAN_BAYRAM: Final = 'ramazan_bayram'
KURBAN_BAYRAM: Final = 'kurban_bayram'

SCHOOLS_CLOSED: Final = 'schools_closed'
SCHOOLS_WINTER_BREAK: Final = 'schools_winter_break'
SCHOOLS_SPRING_BREAK: Final = 'schools_spring_break'
SCHOOLS_SUMMER_BREAK: Final = 'schools_summer_break'
SCHOOLS_AUTUMN_BREAK: Final = 'schools_autumn_break'

BEFORE_AFTER_HOLIDAY: Final = 'before_after_holiday'
BRIDGE_DAY: Final = 'bridge_day'

DAILY: Final = 'daily'
HOURLY: Final = 'hourly'

TRAIN: Final = 'train'
TEST: Final = 'test'
VALIDATION: Final = 'validation'

YEAR_MOD: Final = 'year_mod'
WEEK_DAY_SINE: Final = 'week_day_sine'
WEEK_DAY_COS: Final = 'week_day_cos'
MONTH_SINE: Final = 'month_sine'
MONTH_COS: Final = 'month_cos'
DAY_SINE: Final = 'day_sine'
DAY_COS: Final = 'day_cos'
QUARTER_SINE: Final = 'quarter_sine'
QUARTER_COS: Final = 'quarter_cos'
HOUR_SINE: Final = 'hour_sine'
HOUR_COS: Final = 'hour_cos'

MIN: Final = 'min'
MAX: Final = 'max'
AVERAGE: Final = 'average'

MEAN: Final = 'mean'
STD: Final = 'std'

START: Final = 'start'
END: Final = 'end'

TRAIN_BATCH_SIZE: Final = 'train_batch_size'
VALIDATION_BATCH_SIZE: Final = 'validation_batch_size'
NUMBER_OF_EPOCHS: Final = 'n_epochs'

INPUT_SEQUENCE_LENGTH: Final = 'input_sequence_length'
OUTPUT_SEQUENCE_LENGTH: Final = 'output_sequence_length'
HIDDEN_LAYER_SIZE: Final = 'hidden_layer_size'
NUMBER_OF_ENCODER_LAYERS: Final = 'number_of_encoder_layers'
TEACHER_FORCING_PROB: Final = 'teacher_forcing_prob'
INPUT_VECTOR_LENGTH: Final = 'input_vector_length'

